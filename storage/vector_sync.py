import asyncio
import json
import os
import sys
import time
from dotenv import load_dotenv

# Initialize paths and env
load_dotenv()
os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ["PATH"]
sys.path.append(os.getcwd())

from context.vector_store import VectorStore, SemanticCodeSplitter
from context.mcp_client import MCPClient
from context.retrievers.github_retriever import GitHubRetriever

# Common source extensions to index
SOURCE_EXTENSIONS = {".py", ".js", ".ts", ".go", ".sql", ".md"}
MAX_DEPTH = 3 

async def crawl_repo_recursive(mcp_client, owner, repo, path="", depth=0):
    """Recursively crawls a repository with JSON parsing fix."""
    if depth > MAX_DEPTH:
        return []
        
    print(f"  📂 Crawling: {path if path else '/'}")
    files_found = []
    
    try:
        # get_file_contents returns a CallToolResult
        result = await mcp_client.call_tool(
            "github", 
            "get_file_contents", 
            {"owner": owner, "repo": repo, "path": path}
        )
        
        # Friendly rate-limit delay
        time.sleep(0.5)

        # FIX: The response from MCP is a list of TextContent objects. The text is a JSON string.
        if hasattr(result, "content") and result.content:
            raw_text = result.content[0].text
            try:
                items = json.loads(raw_text)
                if isinstance(items, list):
                    for item in items:
                        item_path = item["path"]
                        if item["type"] == "dir":
                            if any(x in item_path.lower() for x in ["node_modules", ".git", "__pycache__", "venv", "dist"]):
                                continue
                            subdir_files = await crawl_repo_recursive(mcp_client, owner, repo, item_path, depth + 1)
                            files_found.extend(subdir_files)
                        elif item["type"] == "file":
                            if any(item_path.endswith(ext) for ext in SOURCE_EXTENSIONS):
                                files_found.append(item_path)
                                
            except json.JSONDecodeError:
                # If it's not a list, it might be the actual file content (if we hit a file directly)
                pass
            
    except Exception as e:
        print(f"    ⚠️ Error in {path}: {e}")
        
    return files_found[:50]

async def sync_all_projects_deep_crawl():
    print("🧠 Starting FIXED DEEP CRAWLER Sync...")
    status_file = "storage/sync_status.txt"
    
    mcp_client = MCPClient()
    gh = GitHubRetriever(mcp_client)
    store = VectorStore()
    splitter = SemanticCodeSplitter()

    try:
        await gh.connect()
        
        registry_path = "storage/project_registry.json"
        with open(registry_path, "r") as f:
            projects = json.load(f)

        print(f"📊 Found {len(projects)} projects.")

        for i, project in enumerate(projects):
            repo_id = project["id"]
            owner = project.get("owner", "pranaya-mathur")
            repo_name = project["name"] 
            
            with open(status_file, "w") as sf:
                sf.write(f"PROG: {i+1}/{len(projects)} | CURRENT: {repo_name}")

            print(f"\n📂 [{i+1}/{len(projects)}] Indexing: {repo_name}...")
            
            try:
                files_to_index = await crawl_repo_recursive(mcp_client, owner, repo_name, depth=0)
                print(f"  ✨ Local discovery found {len(files_to_index)} files.")
                
                for path in files_to_index:
                    try:
                        file_result = await mcp_client.call_tool(
                            "github", 
                            "get_file_contents", 
                            {"owner": owner, "repo": repo_name, "path": path}
                        )
                        
                        if hasattr(file_result, "content") and file_result.content:
                            # Parse file content
                            file_info = json.loads(file_result.content[0].text)
                            if "content" in file_info:
                                content = file_info["content"]
                                chunks = splitter.split(content, path)
                                metadata = [{
                                    "repo": repo_name,
                                    "path": path,
                                    "project_id": repo_id
                                } for _ in chunks]
                                
                                store.upsert_code_chunks(chunks, metadata)
                                print(f"    ✅ Indexed: {path}")
                                
                        time.sleep(0.5)
                        
                    except Exception as e:
                        print(f"    ⚠️ Fail {path}: {e}")
                            
            except Exception as e:
                print(f"  ❌ Repo Error {repo_name}: {e}")

        print("\n🏆 CRAWL SUCCESSFUL! Your brain is now technically loaded.")

    except Exception as e:
        print(f"❌ Critical Error: {e}")
    finally:
        await mcp_client.disconnect_all()

if __name__ == "__main__":
    asyncio.run(sync_all_projects_deep_crawl())
