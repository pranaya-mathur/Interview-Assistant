import os
from context.mcp_client import MCPClient

class GitRetriever:
    """Retrieves local repository context using the Git MCP server."""
    
    def __init__(self, client: MCPClient):
        self.client = client
        self.server_name = "git"
        # Default to current project root
        self.repo_path = os.path.abspath(os.getcwd())

    async def connect(self):
        """Connects to the Git MCP server."""
        # Note: Using uvx (official recommendation) to run the git server
        command = "/opt/homebrew/bin/uv"
        args = ["tool", "run", "mcp-server-git", "--repository", self.repo_path]
        await self.client.connect_to_server(self.server_name, command, args)

    async def search_files(self, query: str):
        """Searches for files in the local repository."""
        if self.server_name not in self.client.sessions:
            return "Git MCP not connected."
            
        return await self.client.call_tool(
            self.server_name, 
            "search_files", 
            {"query": query}
        )

    async def get_commit_history(self, n: int = 5):
        """Retrieves the last N commits."""
        if self.server_name not in self.client.sessions:
            return "Git MCP not connected."
            
        return await self.client.call_tool(
            self.server_name, 
            "get_commit_history", 
            {"n": n}
        )
