from .util import tool_name, tool_method, tool_class, method_arg
from .tool import Tool

@tool_class(name = "Chat Interface", desc = "Allows you to interact with the instant messaging system to perform actions and search through conversation histories")
class ChatTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tool_method(desc = 'Search the conversation history of public message channels')
    @method_arg(name = 'query', type = str, desc = 'Phrase to search for in the chat server history')
    def search(self, **kwargs): pass

    @tool_method(desc = 'Send a message to a given user')
    @method_arg(name = 'user_name', type = str, desc = 'Name of the user to deliver the message to')
    @method_arg(name = 'message', type = str, desc = 'Message to deliver to the user')
    def message(self, **kwargs): pass
