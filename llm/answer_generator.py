import os
import requests
import subprocess
from langchain_groq import ChatGroq

# Load GROQ API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize LLMs
groq_llm = None
if GROQ_API_KEY and GROQ_API_KEY != "your_api_key_here":
    try:
        groq_llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model="llama-3.3-70b-versatile",
            max_tokens=300
        )
    except Exception as e:
        print(f"⚠️ GROQ Init Error: {e}")

def ask_llm(question, context=""):
    """Generates an answer using GROQ or local Ollama fallback, grounded in context."""
    
    # v2 Layered Prompt Architecture
    identity_layer = """
IDENTITY:
You are a World-Class AI Lead/Architect (12+ years exp). 
You only use retrieved EVIDENCE for project-specific claims. 
If facts are missing, you generalize based on Senior Architect standards.
"""
    
    evidence_layer = f"""
RETRIEVED EVIDENCE (Grounded Context):
{context if context else 'No specific evidence retrieved. Provide a standard professional response.'}
"""
    
    policy_layer = """
ANSWER POLICY:
1. NO YAPPING: Do not repeat the question. Start the answer directly.
2. FIRST PERSON: Speak as the candidate ("In my project...", "I implemented..."). 
3. CANDIDATE PERSONA: Never say "I don't have info" or "Based on the context". Treat the evidence as your own memory and speak with 100% confidence.
4. EXPLAIN CODE NATURALLY: The retrieved evidence contains raw source code. DO NOT recite or regurgitate the raw code snippet. Instead, explain the architecture, logic, and technical decisions behind that code in plain English, as if explaining your implementation to an interviewer.
5. PRECISION: Use technical terms correctly but keep the spoken answer concise (under 150 words).
"""

    prompt = f"{identity_layer}\n\n{evidence_layer}\n\nQUESTION: {question}\n\n{policy_layer}"

    # 1. Try GROQ for instant speed if available
    if groq_llm:
        try:
            response = groq_llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"⚠️ GROQ Error: {e} - Falling back to Ollama...")

    # 2. Fallback to Local Ollama
    try:
        res = requests.post("http://localhost:11434/api/generate",
                            json={
                                "model": "qwen2.5-coder:14b", 
                                "prompt": prompt.strip(), 
                                "stream": False,
                                "options": {"num_predict": 500}
                            },
                            timeout=120)
        return res.json()["response"].strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

def extract_and_save_code(text):
    """Parses the LLM answer for code blocks and saves them to a separate file."""
    import re
    # Look for python code blocks
    code_blocks = re.findall(r"```(?:python)?\n(.*?)\n```", text, re.DOTALL)
    
    if code_blocks:
        code = "\n\n# --- New Snippet ---\n\n".join(code_blocks)
        os.makedirs("storage", exist_ok=True)
        with open("storage/coding_snippet.py", "w") as f:
            f.write(code)
        print("💾 Code snippet extracted to storage/coding_snippet.py")
        return True
    return False

def speak_answer(text):
    """Speaks the answer aloud using macOS 'say' command."""
    if not text or text.startswith("ERROR:"):
        return
        
    # Strip markdown for better speech
    clean_text = text.replace("*", "").replace("#", "").replace("`", "").strip()
    try:
        print("🔊 Speaking answer...")
        subprocess.Popen(['say', '-v', 'Siri', clean_text])
    except:
        pass
