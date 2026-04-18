import os
from context.mcp_client import MCPClient

class GitHubRetriever:
    """Retrieves repository context using the GitHub MCP server."""
    
    def __init__(self, client: MCPClient):
        self.client = client
        self.server_name = "github"
        self.token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

    async def connect(self):
        """Connects to the GitHub MCP server."""
        if not self.token or self.token == "your_github_pat_here":
            print("⚠️ GitHub Token is still a placeholder. GitHub MCP will be limited or disabled.")
            return

        command = "npx"
        args = ["-y", "@modelcontextprotocol/server-github"]
        env = os.environ.copy()
        env["GITHUB_PERSONAL_ACCESS_TOKEN"] = self.token
        
        await self.client.connect_to_server(self.server_name, command, args, env=env)

    async def get_user_data(self, username: str = "pranaya-mathur"):
        """Fetches profile and repo list for a specific user."""
        if self.server_name not in self.client.sessions:
            return None
            
        try:
            repos = await self.client.call_tool(
                self.server_name, 
                "search_repositories", 
                {"query": f"user:{username}"}
            )
            return repos
        except Exception as e:
            return f"Error fetching GitHub user data: {e}"

    async def get_project_context(self, repo_name: str, owner: str = "pranaya-mathur"):
        """Fetches the README text of a specific repository."""
        if self.server_name not in self.client.sessions:
            return None
            
        try:
            result = await self.client.call_tool(
                self.server_name, 
                "get_file_contents", 
                {"owner": owner, "repo": repo_name, "path": "README.md"}
            )
            # Standard MCP text extraction
            if hasattr(result, 'content') and len(result.content) > 0:
                return result.content[0].text
            return str(result)
        except Exception as e:
            return f"GitHub Error (Repo: {repo_name}): {e}"

    async def search_code(self, q: str):
        """Searches for specific code patterns (e.g. FastAPI, LangGraph) in the user's repos."""
        if self.server_name not in self.client.sessions:
            return None
            
        try:
            # Note: GitHub Code Search usually requires a 'user:' or 'repo:' qualifier for precision
            full_query = f"user:pranaya-mathur {q}"
            result = await self.client.call_tool(
                self.server_name, 
                "search_code", 
                {"q": full_query}
            )
            # Standard MCP text extraction
            if hasattr(result, 'content') and len(result.content) > 0:
                return result.content[0].text
            return str(result)
        except Exception as e:
            return f"GitHub Code Search Error: {e}"
