import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Ensure we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from context.mcp_client import MCPClient
from context.retrievers.github_retriever import GitHubRetriever

load_dotenv()

async def verify():
    # Set PATH for npx
    os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ["PATH"]
    
    client = MCPClient()
    gh = GitHubRetriever(client)
    
    try:
        await gh.connect()
        result = await gh.client.call_tool("github", "search_repositories", {"query": "user:pranaya-mathur"})
        
        # Check result type and content
        print(f"Result Type: {type(result)}")
        if hasattr(result, 'content'):
            print("Content Keys/Structure:")
            print(result.content[0].text[:1000]) # First 1000 chars of JSON/Text
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect_all()

if __name__ == "__main__":
    asyncio.run(verify())
