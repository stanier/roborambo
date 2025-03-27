from .util import tool_name, tool_method, tool_class, method_arg
from .tool import Tool

@tool_class(name = "Knowledgebase Explorer", desc = "Allows you to explore an internal knowledge base")
class KnowledgebaseTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tool_method(desc = 'Search the internal knowledgebase')
    @method_arg(name = 'query', type = str, desc = 'Phrase to search the knowledgebase for')
    def search(self, **kwargs): pass
