from .util import tool_name, tool_method, tool_class, method_arg
from .tool import Tool

@tool_class(name = "GraphQL", desc = "Enables you to submit read-only GraphQL queries to abritrary endpoints")
class GraphQLTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tool_method(desc = 'Query a GraphQL endpoint')
    @method_arg(name = 'endpoint', type = str, desc = 'URI of the endpoint we should talk to')
    @method_arg(name = 'query', type = str, desc = 'GraphQL query to send to the endpoint')
    def query(self, **kwargs): pass

    @tool_method(desc = 'Get more information about a specific GraphQL endpoint')
    @method_arg(name = 'readdocs', type = str, desc = 'URI to the page hosting the endpoint\'s documentation')
    def readdocs(self, **kwargs): pass
