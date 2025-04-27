from ..tools.tool import Tool
from ..tools.util import tool_class, tool_method, method_arg

class MCPToolAdapter:
    """Adapter to convert MCP tools to RoboRambo tools"""
    
    def __init__(self, mcp_host: MCPHost):
        self.mcp_host = mcp_host
        self.connections = {}
        
    async def create_tool_from_mcp(self, server_name: str, tool_info: Dict) -> Tool:
        """Dynamically create a RoboRambo tool from MCP tool definition"""
        
        # Create a dynamic tool class
        class_attrs = {
            '__init__': self._create_init_method(server_name),
        }
        
        # Add method for the MCP tool
        method_attrs = self._create_tool_method(tool_info)
        class_attrs[tool_info['name'].replace('-', '_')] = method_attrs
        
        # Create the tool class
        DynamicMCPTool = type(
            f"MCP_{server_name}_{tool_info['name']}",
            (Tool,),
            class_attrs
        )
        
        # Apply decorators
        @tool_class(name=f"MCP {server_name}: {tool_info['name']}", 
                   desc=tool_info.get('description', ''))
        class DecoratedTool(DynamicMCPTool):
            pass
        
        return DecoratedTool()
    
    def _create_init_method(self, server_name: str):
        """Create init method for dynamic tool"""
        def __init__(self, **kwargs):
            super(type(self), self).__init__(**kwargs)
            self.server_name = server_name
            self.mcp_connection = None
        return __init__
    
    def _create_tool_method(self, tool_info: Dict):
        """Create method for dynamic tool"""
        async def dynamic_method(self, **kwargs):
            if not self.mcp_connection:
                # Establish connection to MCP server
                process = await self.mcp_host.start_server(self.server_name)
                self.mcp_connection = await self.mcp_host.connect_server(
                    self.server_name, process
                )
            
            # Call the MCP tool
            result = await self.mcp_host.call_tool(
                self.mcp_connection,
                tool_info['name'],
                kwargs
            )
            return result
        
        # Apply decorators
        method = tool_method(desc=tool_info.get('description', ''))(dynamic_method)
        
        # Add argument decorators
        for param_name, param_info in tool_info.get('inputSchema', {}).get('properties', {}).items():
            method = method_arg(
                name=param_name,
                type=param_info.get('type', str),
                desc=param_info.get('description', '')
            )(method)
        
        return method