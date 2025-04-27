import asyncio
from .util import tool_class, tool_method, method_arg
from .tool import Tool
from ..mcp.host import MCPHost
from ..mcp.adapter import MCPToolAdapter

@tool_class(name="MCP Manager", desc="Manages Model Context Protocol server connections")
class MCPManagerTool(Tool):
    """Tool for managing MCP connections and dynamically loading MCP tools"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mcp_host = MCPHost()
        self.adapter = MCPToolAdapter(self.mcp_host)
        self.loaded_tools = {}
        
    @tool_method(desc="Discover and load MCP servers")
    def discover_mcp_servers(self, **kwargs):
        """Discover available MCP servers and load their tools"""
        loop = asyncio.get_event_loop()
        servers = loop.run_until_complete(self.mcp_host.discover_servers())
        
        for server_name in servers:
            try:
                process = loop.run_until_complete(self.mcp_host.start_server(server_name))
                connection = loop.run_until_complete(self.mcp_host.connect_server(server_name, process))
                tools = loop.run_until_complete(self.mcp_host.list_tools(connection))
                
                for tool_info in tools:
                    tool_instance = loop.run_until_complete(
                        self.adapter.create_tool_from_mcp(server_name, tool_info)
                    )
                    tool_key = f"{server_name}_{tool_info['name']}"
                    self.loaded_tools[tool_key] = tool_instance
                    
            except Exception as e:
                self.logger.error(f"Failed to load MCP server {server_name}: {e}")
        
        return list(self.loaded_tools.keys())
    
    @tool_method(desc="Get loaded MCP tools")
    def get_loaded_tools(self, **kwargs):
        """Return dictionary of loaded MCP tools"""
        return self.loaded_tools