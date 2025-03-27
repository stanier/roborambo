from inspect import getmembers, ismethod

from .util import tool_name, tool_method, tool_class, method_arg
from ..types import Configable

@tool_class(name = "Base Tool", desc = "Unconfigured base tool")
class Tool(Configable):
    emoji = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in getmembers(self, predicate=ismethod):
            if '__config__' in dir(i[1]) and i[1].__config__.get('method_enabled', False) == True:
                method = {
                    'arguments': {},
                    'method': i[1],
                }
                for j in i[1].__config__['arguments']:
                    method['arguments'][j] = i[1].__config__['arguments'][j]
                self.__config__["tool_methods"][i[0]] = method