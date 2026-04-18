import asyncio
import os
import sys
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Ensure we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from context.mcp_client import MCPClient
from context.retrievers.github_retriever import GitHubRetriever
from context.retrievers.memory_retriever import MemoryRetriever

load_dotenv()

async def sync_github_to_memory():
    """
    Scans GitHub repositories active in the last 5 months 
    and ingests them into the persistent Knowledge Graph.
    """
    print("\n🚀 Starting Dynamic GitHub Memory Sync (Last 5 Months)...")
    
    # Set PATH for npx
    os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ["PATH"]
    
    client = MCPClient()
    gh = GitHubRetriever(client)
    mem = MemoryRetriever(client)
    
    try:
        # 1. Connect to both servers
        await gh.connect()
        await mem.connect()
        
        # 2. Calculate date filter (5 months ago)
        # Using Nov 2025 as the threshold for an April 2026 run
        lookback_date = (datetime.now() - timedelta(days=5*30)).strftime('%Y-%m-%d')
        search_query = f"user:pranaya-mathur pushed:>{lookback_date}"
        print(f"🔍 Searching repos with activity since: {lookback_date}")
        
        # 3. Find Repositories
        result = await gh.client.call_tool(
            "github", 
            "search_repositories", 
            {"query": search_query}
        )
        
        if not hasattr(result, 'content') or not result.content:
            print("⚠️ No repositories found for the search query.")
            return

        # Parse JSON from the first content block
        try:
            raw_data = json.loads(result.content[0].text)
            repos = raw_data.get("items", [])
        except Exception as e:
            print(f"❌ Failed to parse GitHub response: {e}")
            return

        print(f"✅ Found {len(repos)} active repositories.")
        
        # 4. Process Repositories
        for repo in repos:
            name = repo["name"]
            pushed_at = repo["pushed_at"]
            description = repo.get("description", "No description")
            
            print(f"\n📖 Analyzing project: {name} (Last Pushed: {pushed_at})...")
            
            # Fetch README for technical context
            readme = await gh.get_project_context(name)
            
            # Create Entity in Memory Graph
            # We truncate README to stay within reasonable memory/context limits
            clean_readme = readme[:1000] if readme and "Error" not in readme else "No README available."
            
            entity = {
                "name": name,
                "entityType": "Project",
                "observations": [
                    f"Description: {description}",
                    f"Last modified (pushed): {pushed_at}",
                    f"Key Documentation Snippet: {clean_readme}"
                ]
            }
            
            await mem.add_knowledge([entity], [])
            print(f"💾 {name} ingested into Knowledge Graph.")

        print("\n✨ GitHub Memory Sync Complete!")
        
    except Exception as e:
        print(f"❌ Sync Failed: {e}")
    finally:
        await client.disconnect_all()

if __name__ == "__main__":
    asyncio.run(sync_github_to_memory())
