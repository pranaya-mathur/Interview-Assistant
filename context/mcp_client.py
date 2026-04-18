import asyncio
import os
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    """Manages persistent connections to multiple MCP servers via stdio transport."""
    
    def __init__(self):
        self.sessions = {}
        self.exit_stack = AsyncExitStack()
        
        # Ensure common Homebrew/Mac paths are available for Node/NPM
        self.env = os.environ.copy()
        mac_paths = "/opt/homebrew/bin:/usr/local/bin"
        if mac_paths not in self.env["PATH"]:
            self.env["PATH"] = f"{mac_paths}:{self.env['PATH']}"

    async def connect_to_server(self, server_name, command, args, env=None):
        """Starts a server process and establishes a persistent MCP session."""
        if server_name in self.sessions:
            return # Already connected
            
        # Optimization: If using 'npx', try to use local node_modules version instead
        if command == "npx":
            # Map common servers to their local entry points for instant startup
            local_map = {
                "@modelcontextprotocol/server-github": "./node_modules/.bin/mcp-server-github",
                "@modelcontextprotocol/server-filesystem": "./node_modules/.bin/mcp-server-filesystem"
            }
            
            # Check if we are trying to run one of these
            for pkg, local_bin in local_map.items():
                if pkg in args and os.path.exists(local_bin):
                    command = "node"
                    # Pass the entry point directly
                    args = [local_bin] + [a for a in args if a != pkg and a != "-y"]
                    break

        print(f"🔌 Connecting to MCP Server: {server_name}...")
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env if env else self.env
        )
        
        try:
            # Entering the stdio_client context
            read, write = await self.exit_stack.enter_async_context(stdio_client(server_params))
            session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            
            await session.initialize()
            self.sessions[server_name] = session
            print(f"✅ Connected to {server_name} (Ready)")
        except Exception as e:
            print(f"❌ Failed to connect to {server_name}: {e}")
            raise

    async def call_tool(self, server_name, tool_name, arguments):
        """Calls a tool on a specific persistent MCP server."""
        if server_name not in self.sessions:
            raise ValueError(f"Server {server_name} not connected.")
        
        session = self.sessions[server_name]
        return await session.call_tool(tool_name, arguments)

    async def disconnect_all(self):
        """Gracefully disconnects all persistent MCP servers."""
        if self.sessions:
            print("🔌 Disconnecting all MCP servers...")
            await self.exit_stack.aclose()
            self.sessions = {}
