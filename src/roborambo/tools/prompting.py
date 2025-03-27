from .util import tool_name, tool_method, tool_class, method_arg
from .tool import Tool

@tool_class(name = "LLM Prompting Toolkit", desc = "")
class SimplePromptingTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)