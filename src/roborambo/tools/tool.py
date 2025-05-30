from inspect import getmembers, ismethod
from .util import tool_class

@tool_class(name="Base Tool", desc="Unconfigured base tool")
class Tool:
    emoji = None

    def __init__(self, **kwargs):
        if not hasattr(self, '__config__'):
            self.__config__ = {'tool_methods': {}}
        
        # Initialize methods from decorated functions
        for name, method in getmembers(self, predicate=ismethod):
            if hasattr(method, '__config__'):
                # Check if method is enabled (default to True if not specified)
                method_enabled = method.__config__.get('method_enabled', True)
                if method_enabled:
                    method_config = {
                        'arguments': {},
                        'method': method,
                        # Copy method description from decorator
                        'description': method.__config__.get('method_desc', 'No description'),
                        'method_desc': method.__config__.get('method_desc', 'No description'),  # Keep both for compatibility
                    }
                    # Copy argument configurations
                    for arg in method.__config__.get('arguments', {}):
                        method_config['arguments'][arg] = method.__config__['arguments'][arg]
                    self.__config__["tool_methods"][name] = method_config

    @property
    def methods(self):
        """Return configured methods for this tool."""
        return getattr(self, '__config__', {}).get('tool_methods', {})

    @property 
    def name(self):
        """Return tool name from configuration."""
        return getattr(self, '__config__', {}).get('tool_name', self.__class__.__name__)

    @property
    def description(self):
        """Return tool description from configuration.""" 
        return getattr(self, '__config__', {}).get('tool_desc', 'No description available')