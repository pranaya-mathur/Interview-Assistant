import asyncio
import os
from context.mcp_client import MCPClient
from context.retrievers.github_retriever import GitHubRetriever
from dotenv import load_dotenv

load_dotenv()

async def list_active_repos():
    client = MCPClient()
    gh = GitHubRetriever(client)
    
    try:
        await gh.connect()
        # Search for repos belonging to the user
        result = await gh.get_user_data("pranaya-mathur")
        
        # In a real tool call, result.content would have the JSON
        # For research, let's just print the raw result
        print("REPOS FOUND:")
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect_all()

if __name__ == "__main__":
    asyncio.run(list_active_repos())
