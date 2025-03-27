from .util import tool_name, tool_method, tool_class, method_arg
from .tool import Tool

@tool_class(name = "Schedule Tool (internal)", desc = "A tool that allows you to create and check schedules, including leaving notes about things that should be done at specific times")
class InternalScheduleTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tool_method(desc = 'Look for time in a schedule to dedicate to something')
    @method_arg(name = 'window', type = str, desc = 'Timeframe that the allocated timeslot should fall within')
    @method_arg(name = 'duration', type = str, desc = 'How much time needs to be set aside')
    def find_time(self, **kwargs): pass

    @tool_method(desc = 'Look for something in the schedule')
    @method_arg(name = 'query', type = str, desc = 'Query to lookup')
    def lookup(self, **kwargs): pass

    @tool_method(desc = '')
    @method_arg(name = '', type = None, desc = '')
    def add(self, **kwargs): pass

    @tool_method(desc = '')
    @method_arg(name = '', type = None, desc = '')
    def remove(self, **kwargs): pass
