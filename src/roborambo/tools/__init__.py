import re
from .tool import Tool
from .inspector import InspectorTool
from .web import WebTool

def parse_invocation(invocation, **kwargs):
    if "INVOKE" not in invocation[0:6]: 
        return False
    
    match = re.search(r"^INVOKE\s(\w+)\.(\w+)\((.+)\)", invocation)
    if not match:
        return False

    tool_args = {}
    for arg in re.findall(r"(?i)(\w+)\s?\=\s?(?:((?:true)|(?:false))|('[^'\|\n)]+')|(\"[^\"\|\n)]+\")|(\[.*\])|(\{.*\})|(\d+.\d+)|(\w+))?", match.group(3)):
        if arg[1]:  # Boolean
            value = (arg[1].lower() == 'true')
        if arg[2] or arg[3]:  # String
            value = (arg[2] + arg[3])[1:-1]
        if arg[4]:  # Array/list
            value = arg[4][1:-1]
        if arg[5]:  # Object
            value = arg[5][1:-1]
        if arg[6]:  # Float
            value = float(arg[6])
        if arg[7] and arg[7].isnumeric():  # Int
            value = int(arg[7])

        tool_args[arg[0]] = value
    
    return {'tool': match.group(1), 'func': match.group(2), 'args': tool_args}

available_tools = {
    'inspector': InspectorTool,
    'web': WebTool,
}