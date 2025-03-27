from .util import tool_name, tool_method, tool_class, method_arg
from .tool import Tool

@tool_class(name = "LLM Prompting Toolkit", desc = "")
class SimplePromptingTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tool_method(desc = '')
    @method_arg(name = 'image_uri', type = str, desc = '')
    @method_arg(name = 'prompt', type = str, desc = '')
    def interpret(self, **kwargs):
        pass

    @tool_method(desc = '')
    @method_arg(name = 'prompt', type = str, desc = '')
    @method_arg(name = 'negative_prompt', type = str, desc = '')
    def generate(self, **kwargs):
        pass