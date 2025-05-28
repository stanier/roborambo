from .tool import Tool
from .inspector import InspectorTool
from .web import WebTool
from .test import TestTool

# Available tools registry
available_tools = {
    'inspector': InspectorTool,
    'web': WebTool,
    'test': TestTool,
}