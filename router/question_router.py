import os
import json
from langchain_groq import ChatGroq

class QuestionRouter:
    """Classifies interview questions and extracts target project IDs for selective grounding."""
    
    def __init__(self):
        self.classes = {
            "PROJECT": "Questions about specific past projects, architecture of your work, or tech stacks used.",
            "RESUME": "Questions about your background, experience walk-through, or specific roles.",
            "TECHNICAL": "General computer science or AI theory (no coding requested).",
            "CODING": "Requests for code implementation, algorithms, or snippets (e.g., 'Write a binary search').",
            "SYSTEM_DESIGN": "Hypothetical design questions (e.g., 'Design a YouTube clone').",
            "BEHAVIORAL": "Soft skills, conflict resolution, or leadership questions (STAR method).",
            "FOLLOW_UP": "Context-dependent questions like 'Why did you choose that?' or 'What happened then?'"
        }
        
        # Load registry for matching
        self.registry_path = "storage/project_registry.json"
        self.registry = []
        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r") as f:
                self.registry = json.load(f)
        
        # Initialize Groq for high-precision classification
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.llm = None
        if self.groq_api_key:
            try:
                self.llm = ChatGroq(
                    api_key=self.groq_api_key,
                    model="llama-3.3-70b-versatile",
                    max_tokens=50,
                    temperature=0
                )
            except:
                pass

    def classify(self, question: str):
        """Uses GROQ to classify the question and extract a project ID if applicable."""
        desc_list = "\n".join([f"- {k}: {v}" for k, v in self.classes.items()])
        registry_list = "\n".join([f"- {p['name']} (ID: {p['id']})" for p in self.registry])
        
        prompt = f"""
Analyze the interview question below. 

1. Identify the CATEGORY from the list below.
2. If the question mentions a specific PROJECT from the registry, identify its ID.

CATEGORIES:
{desc_list}

PROJECT REGISTRY:
{registry_list}

QUESTION: "{question}"

Output Format: CATEGORY | PROJECT_ID (or 'NONE')
Example: PROJECT | nyaysetu
CATEGORY:"""

        if self.llm:
            try:
                response = self.llm.invoke(prompt)
                result = response.content.strip().upper()
                
                # Default values
                category = "TECHNICAL"
                project_id = None
                
                if "|" in result:
                    parts = result.split("|")
                    res_cat = parts[0].strip()
                    res_id = parts[1].strip()
                    
                    # Validate Category
                    for key in self.classes.keys():
                        if key in res_cat:
                            category = key
                            break
                    
                    # Validate Project ID
                    if res_id != "NONE":
                        # Check if ID exists in registry
                        for p in self.registry:
                            if p["id"].upper() == res_id:
                                project_id = p["id"]
                                break
                
                return category, project_id
            except:
                pass
        
        # Rule-based fuzzy fallback (Improved)
        import re
        q_lower = question.lower()
        found_id = None
        
        # Decide category for fallback
        category = "TECHNICAL"
        if "write" in q_lower or "code" in q_lower or "implement" in q_lower or "algorithm" in q_lower:
            category = "CODING"
        
        for p in self.registry:
            name_clean = p["name"].lower().replace("-", " ").replace("_", " ")
            id_clean = p["id"].lower().replace("_", " ")
            
            # Look for project name or ID as keywords in the question
            pattern = rf"\b({re.escape(name_clean)}|{re.escape(id_clean)}|{re.escape(p['id'])})\b"
            if re.search(pattern, q_lower):
                return category, p["id"]
            
            # Even more fuzzy substrings
            if name_clean in q_lower or id_clean in q_lower:
                found_id = p["id"]
                
        return category, found_id
