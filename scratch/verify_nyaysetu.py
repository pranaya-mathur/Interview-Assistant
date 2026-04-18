import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.getcwd())

from context.mcp_client import MCPClient
from context.retrievers.memory_retriever import MemoryRetriever

async def verify_nyaysetu():
    print("🕵️ Forensic Memory Check: Nyaysetu")
    os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ["PATH"]
    
    client = MCPClient()
    mem = MemoryRetriever(client)
    
    try:
        await mem.connect()
        # Search for nyaysetu
        result = await mem.search_memory("nyaysetu")
        
        print("\n--- RAW MEMORY RESULT ---")
        print(result)
        print("-------------------------")
        
        if result and "nyaysetu" in str(result).lower():
            print("✅ SUCCESS: Nyaysetu is indexed in the Knowledge Graph.")
        else:
            print("❌ FAILURE: Nyaysetu NOT found in Memory Graph.")
            
    except Exception as e:
        print(f"❌ Critical Error: {e}")
    finally:
        await client.disconnect_all()

if __name__ == "__main__":
    asyncio.run(verify_nyaysetu())
