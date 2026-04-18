import asyncio
import os
import sys
import json
import re
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.getcwd())

from context.mcp_client import MCPClient
from context.retrievers.memory_retriever import MemoryRetriever

async def generate_registry():
    """Pulls all project entities from memory and creates a lightweight registry JSON."""
    print("📋 Generating Project Registry from Memory...")
    os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ["PATH"]
    
    client = MCPClient()
    mem = MemoryRetriever(client)
    
    try:
        await mem.connect()
        # Fetch the entire graph (already returns text)
        raw_text = await mem.get_graph()
        
        registry = []
        
        # Extract individual entity objects from the raw JSON/Text output
        # The output of get_graph in the memory-mcp-server is usually a JSON-like string
        # representing the entities and relations.
        
        # Use regex to find project entity blocks
        # We look for "name" and "entityType": "Project"
        entities_match = re.search(r'"entities":\s*\[(.*?)\]', raw_text, re.DOTALL)
        if entities_match:
            entities_raw = entities_match.group(1)
            # Find individual objects in the list
            entity_blocks = re.findall(r'\{(.*?)\}', entities_raw, re.DOTALL)
            
            for block in entity_blocks:
                if '"entityType": "Project"' in block or '"entityType":"Project"' in block:
                    name_match = re.search(r'"name":\s*"([^"]+)"', block)
                    if name_match:
                        name = name_match.group(1)
                        # Find Description in observations
                        desc_match = re.search(r'"Description:\s*([^"]+)"', block)
                        one_liner = desc_match.group(1) if desc_match else "A project in your portfolio."
                        
                        registry.append({
                            "id": name.lower().replace("-", "_"),
                            "name": name,
                            "summary": one_liner
                        })
        
        if not registry:
            # Fallback: if entities list wasn't found, try flat search
            flat_matches = re.findall(r'"name":\s*"([^"]+)"[^{}]*"entityType":\s*"Project"', raw_text, re.DOTALL)
            for name in flat_matches:
                registry.append({
                    "id": name.lower().replace("-", "_"),
                    "name": name,
                    "summary": "Project in your portfolio."
                })

        if not registry:
            print("⚠️ No project entities found in Knowledge Graph.")
            return

        os.makedirs("storage", exist_ok=True)
        # Deduplicate
        seen = set()
        unique_registry = []
        for p in registry:
            if p["id"] not in seen:
                unique_registry.append(p)
                seen.add(p["id"])

        with open("storage/project_registry.json", "w") as f:
            json.dump(unique_registry, f, indent=2)
            
        print(f"✅ Registry generated with {len(unique_registry)} projects at storage/project_registry.json")
        
    except Exception as e:
        print(f"❌ Failed to generate registry: {e}")
    finally:
        await client.disconnect_all()

if __name__ == "__main__":
    asyncio.run(generate_registry())
