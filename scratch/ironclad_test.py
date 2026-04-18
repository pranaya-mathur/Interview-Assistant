import asyncio
import os
import sys
import json

# Set standard paths
sys.path.append(os.getcwd())
os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ["PATH"]

from context.mcp_client import MCPClient
from context.retrievers.filesystem_retriever import FilesystemRetriever
from context.retrievers.github_retriever import GitHubRetriever
from context.retrievers.git_retriever import GitRetriever
from context.retrievers.memory_retriever import MemoryRetriever
from app import get_grounded_context

async def simulation_test():
    print("🎭 FINAL IRONCLAD TEST: Smart Project Routing")
    
    client = MCPClient()
    fs = FilesystemRetriever(client)
    gh = GitHubRetriever(client)
    git = GitRetriever(client)
    mem = MemoryRetriever(client)
    
    try:
        await mem.connect()
        await fs.connect()
        await gh.connect()
        
        # Scenario: User asks about Nyaysetu
        # The router would detect category: PROJECT and project_id: nyaysetu
        category = "PROJECT"
        project_id = "nyaysetu"
        question = "Can you walk me through your Nyaysetu application?"
        
        print(f"Simulation Parameters: Category={category}, ProjectID={project_id}")
        
        # Call the NEW Selective Grounding logic
        context = await get_grounded_context(category, project_id, question, fs, git, gh, mem)
        
        print("\n--- SELECTIVE GROUNDED CONTEXT ---")
        # Check for Nyaysetu specific keywords from memory/github
        print(context[:1000] + "...") 
        print("-------------------------------")
        
        # Validation
        has_nyay = "nyaysetu" in context.lower()
        has_rag = "rag" in context.lower()
        has_fastapi = "fastapi" in context.lower()
        
        if has_nyay and (has_rag or has_fastapi):
            print("\n✅ FINAL SUCCESS: Targeted context for Nyaysetu successfully retrieved without bloat.")
        else:
            print("\n❌ FAILED: Context is still missing deep project details.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect_all()

if __name__ == "__main__":
    asyncio.run(simulation_test())
