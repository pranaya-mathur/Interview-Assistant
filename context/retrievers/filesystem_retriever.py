import os
from context.mcp_client import MCPClient

class FilesystemRetriever:
    """Retrieves context from local files using the Filesystem MCP server."""
    
    def __init__(self, client: MCPClient):
        self.client = client
        self.server_name = "filesystem"
        # Root path for all project assets
        self.root_path = os.path.abspath(os.getcwd())

    async def connect(self):
        """Connects to the Filesystem MCP server restricted to the project root."""
        command = "npx"
        args = ["-y", "@modelcontextprotocol/server-filesystem", self.root_path]
        await self.client.connect_to_server(self.server_name, command, args)

    async def get_prep_file(self, filename: str):
        """Reads a specific file and returns its text content."""
        full_path = os.path.join(self.root_path, filename)
        try:
            result = await self.client.call_tool(
                self.server_name, 
                "read_file", 
                {"path": full_path}
            )
            # Extract text from CallToolResult (MCP SDK structure)
            if hasattr(result, 'content') and len(result.content) > 0:
                return result.content[0].text
            return str(result)
        except Exception as e:
            return f"Error reading {filename}: {e}"

    async def list_prep_files(self, sub_path: str = "."):
        """Lists files available in a specific subdirectory."""
        full_path = os.path.join(self.root_path, sub_path)
        try:
            result = await self.client.call_tool(
                self.server_name, 
                "list_directory", 
                {"path": full_path}
            )
            return result
        except Exception as e:
            return f"Error listing {sub_path}: {e}"
