from .util import tool_name, tool_method, tool_class, method_arg
from .tool import Tool

@tool_class(name = "Tool Inspector", desc = "Allows you to gather further insight into tools.")
class InspectorTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tool_method(enabled = True)
    @tool_method(desc = 'Get more information about a given tool, including available functions and their arguments.  (Hint: `inspector.inspect(tool_slug = "web")`)')
    @method_arg(name = 'tool_slug', type = str, desc = 'The slug used to refer to the tool that should be described.')
    def inspect(self, **kwargs):
        target_tool = active_tools[kwargs.get('tool_slug', 'inspector')]

        funcs_concat = ""
        for func in target_tool['functions']: # functions are required
            args_concat = ""
            for arg in target_tool['functions'][func].get('arguments', {}): # arguments are optional
                args_concat = "{}\n{}".format(args_concat, options['ARGS_ENTRY_TEMPLATE'].format(
                    arg_slug = arg,
                    arg_type = target_tool['functions'][func]['arguments'][arg]['type'],
                    arg_desc = target_tool['functions'][func]['arguments'][arg]['description'],
                ))
            funcs_concat = "{}{}".format(funcs_concat, options['FUNC_ENTRY_TEMPLATE'].format(
                func_slug = func,
                func_desc = target_tool['functions'][func]['description'],
                tool_slug = tool,
                arg_entries = args_concat,
            ))

        tool_string = "```\n{}```".format(options['TOOL_ENTRY_TEMPLATE'].format(
            tool_name = target_tool['name'],
            tool_desc = target_tool['description'],
            func_entries = funcs_concat,
        ))

        return tool_string

    @tool_method(desc = '')
    @method_arg(name = 'tool_slug', type = str, desc = 'The slug used to refer to the tool that should be described')
    def describe(self, **kwargs): pass
