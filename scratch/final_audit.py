import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Ensure we can import from the root
sys.path.append(os.getcwd())

from context.mcp_client import MCPClient
from context.retrievers.github_retriever import GitHubRetriever
from context.retrievers.memory_retriever import MemoryRetriever
from router.question_router import QuestionRouter

async def final_audit():
    print("🕵️ Final Audit: System Sanity Check")
    os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ["PATH"]
    
    client = MCPClient()
    gh = GitHubRetriever(client)
    mem = MemoryRetriever(client)
    router = QuestionRouter()
    
    success_count = 0
    total_checks = 4
    
    try:
        # Check 1: Connectivity
        print("\n1. Testing Connectivity...")
        await gh.connect()
        await mem.connect()
        if 'github' in client.sessions and 'memory' in client.sessions:
            print("✅ Connectivity: SUCCESS (GitHub, Memory)")
            success_count += 1
        else:
            print("❌ Connectivity: FAILED")
            
        # Check 2: Memory Grounding
        print("\n2. Testing Memory retrieval (Nyaysetu)...")
        result = await mem.search_memory("Nyaysetu")
        if result and "Nyaysetu" in str(result):
            print("✅ Memory Grounding: SUCCESS")
            success_count += 1
        else:
            print("⚠️ Memory Grounding: WARNING (No results found, sync might be needed)")

        # Check 3: Router Precision
        print("\n3. Testing Router Precision (Coding)...")
        category = router.classify("Can you write a binary search?")
        if category == "CODING":
            print("✅ Router Precision: SUCCESS")
            success_count += 1
        else:
            print(f"⚠️ Router Precision: WARNING (Detected {category} instead of CODING)")

        # Check 4: GitHub Code Search
        print("\n4. Testing GitHub Code Search...")
        code_result = await gh.search_code("FastAPI")
        if code_result and "Error" not in str(code_result):
            print("✅ GitHub Code Search: SUCCESS")
            success_count += 1
        else:
            print(f"⚠️ GitHub Code Search: WARNING (Result: {code_result})")

        print(f"\nAudit Finished: {success_count}/{total_checks} Checks Passed.")
        
    except Exception as e:
        print(f"❌ Audit Critical Failure: {e}")
    finally:
        await client.disconnect_all()

if __name__ == "__main__":
    asyncio.run(final_audit())
