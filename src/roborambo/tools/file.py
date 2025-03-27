from .util import tool_name, tool_method, tool_class, method_arg
from .tool import Tool

@tool_class(name = "File Browser", desc = "Allows you to search for, read and write files locally")
class FileTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tool_method(desc = 'Search for a given filename')
    @method_arg(name = 'scope', type = str, desc = 'Pathname of filesystem directory the search should occur within')
    @method_arg(name = 'query', type = str, desc = 'Part of the filename being searched for')
    def search(self, **kwargs): pass

    @tool_method(desc = 'Read a given filename')
    @method_arg(name = 'filename', type = str, desc = 'Pathname of the file to read')
    def read(self, **kwargs): pass

    @tool_method(desc = 'Write content to a given filepath')
    @method_arg(name = 'filename', type = str, desc = 'Pathname of the file to write')
    def write(self, **kwargs): pass

    @tool_method(desc = 'Get more information about a file (including it\'s content type)')
    @method_arg(name = 'filename', type = str, desc = 'Pathname of the file to write')
    def identify(self, **kwargs): pass