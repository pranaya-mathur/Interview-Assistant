import json
from context.mcp_client import MCPClient

class MemoryRetriever:
    """Maintains persistent interview context using the Memory MCP server."""
    
    def __init__(self, client: MCPClient):
        self.client = client
        self.server_name = "memory"

    async def connect(self):
        """Connects to the Memory MCP server."""
        command = "npx"
        args = ["-y", "@modelcontextprotocol/server-memory"]
        await self.client.connect_to_server(self.server_name, command, args)

    async def add_knowledge(self, entities: list, relations: list):
        """Adds knowledge to the memory graph."""
        if self.server_name not in self.client.sessions:
            return None
            
        return await self.client.call_tool(
            self.server_name, 
            "create_entities", 
            {"entities": entities}
        )

    async def search_memory(self, query: str):
        """Searches memory and returns a formatted string of nodes and edges."""
        if self.server_name not in self.client.sessions:
            return ""
            
        try:
            result = await self.client.call_tool(
                self.server_name, 
                "search_nodes", 
                {"query": query}
            )
            # Standardize text extraction
            if hasattr(result, 'content') and len(result.content) > 0:
                return result.content[0].text
            return str(result)
        except Exception as e:
            return f"Memory Search Error: {e}"
        
    async def get_graph(self):
        """Retrieves and formats the full knowledge graph."""
        if self.server_name not in self.client.sessions:
            return None
            
        try:
            result = await self.client.call_tool(
                self.server_name, 
                "read_graph", 
                {}
            )
            return str(result)
        except Exception as e:
            return f"Memory Graph Error: {e}"
