from .util import tool_name, tool_method, tool_class, method_arg
from .tool import Tool

@tool_class(name="Tool Inspector", desc="Allows you to gather further insight into tools.")
class InspectorTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tool_method(enabled=True)
    @tool_method(desc='Get more information about a given tool, including available functions and their arguments. (Hint: `inspector.inspect(tool_slug = "web")`)')
    @method_arg(name='tool_slug', type=str, desc='The slug used to refer to the tool that should be described.')
    def inspect(self, **kwargs):
        from . import available_tools
        
        tool_slug = kwargs.get('tool_slug', 'inspector')
        if tool_slug not in available_tools:
            return f"Tool '{tool_slug}' not found. Available tools: {', '.join(available_tools.keys())}"
        
        tool_class = available_tools[tool_slug]
        tool_instance = tool_class()
        
        # Basic tool information
        tool_info = f"**{tool_class.__name__}**\n"
        tool_info += f"Description: {getattr(tool_class, '__doc__', 'No description available')}\n\n"
        
        # List methods
        tool_info += "Available methods:\n"
        for method_name in dir(tool_instance):
            if not method_name.startswith('_') and callable(getattr(tool_instance, method_name)):
                method = getattr(tool_instance, method_name)
                if hasattr(method, '__config__'):
                    tool_info += f"  - {method_name}: {method.__config__.get('method_desc', 'No description')}\n"
        
        return tool_info