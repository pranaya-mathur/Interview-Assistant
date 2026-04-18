import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.getcwd())

from context.mcp_client import MCPClient
from context.retrievers.memory_retriever import MemoryRetriever

async def check_graph():
    os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ["PATH"]
    client = MCPClient()
    mem = MemoryRetriever(client)
    try:
        await mem.connect()
        res = await mem.get_graph()
        print(res.content[0].text[:5000])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect_all()

if __name__ == "__main__":
    asyncio.run(check_graph())
