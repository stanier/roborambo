from .util import tool_name, tool_method, tool_class, method_arg
from .tool import Tool

@tool_class(name = "Ask An Expert", desc = "Allows you to ask an expert for input on a question or topic, in natural language")
class ExpertAskTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tool_method(desc = 'Ask an expert')
    @method_arg(name = 'query', type = str, desc = 'Question to ask')
    def ask(self, **kwargs): pass