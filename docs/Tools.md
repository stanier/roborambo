# Tools

Available tools:
* `inspector`
* `web`

Planned tools:
* `file`
* `scheduler`
* `image`
* `chat`
* `graphql`
* `knowledgebase`
* `prompting`
* `vectorstore`

## Creating tools

### Simple

The tool system is designed to be as frictionless as possible to prevent code redundancy and promote rapid prototyping/adoption.  Here is an example of what a basic tool with one method that takes two arguments looks like:

```python
from .util import tool_name, tool_method, tool_class, method_arg
from .tool import Tool

@tool_class(name = "Example Tool", desc = "Used merely for demonstration purposes")
class ExampleTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tool_method(desc = 'Append second string to first string')
    @method_arg(name = 'foo', type = str, desc = 'String to be appended')
    @method_arg(name = 'bar', type = str, desc = 'String to append')
    def search(self, **kwargs):
        return self.concat_strings(kwargs['foo'], kwargs['bar'])

    def concat_strings(foo, bar):
        return f"{foo}{bar}"
```

From this example, it should be observed that any given Tool is merely a class that has been wrapped with a `@tool_class` decorator.  This decorator specifies basic information about the tool such as it's name, description, and whether or not is enabled.

Within this class, we have two methods.  The method `search` is wrapped with a `@tool_method` to register it as a method of the parent tool.  Without this decorator, the method will not be registered and is not visible to the agent or any other component of the tool pipeline.  Despite this, it can of course still be called by another method internal to the class object.

Beyond this, we also introduce a `@method_arg` decorator to wrap methods.  Information passed into this decorator will be used to construct a dictionary of arguments that the wrapped method can accept, which is visible to the tool pipeline.

Tools, methods, and arguments can each be enabled/disabled individually in the tool definition by passing the `enabled` keyword argument to the decorator.

`@tool_method` and `@tool_class` should each be generally stackable (meaning you can have one line that reads `@tool_method(enabled = True)` and another line for that same method that reads `@tool_method(name = "Foobar")`, with the tooling system attempting to apply information from each decorator [first come first serve with definitions currently]).  Caveat to this is that it might not work exactly as expected, such as in cases of a decorator with no arguments followed by a decorator containing arguments...  I've already lost a weekend fixing up the decorator implementation, I don't feel like losing any more time to attempt resolving this presently.

### Advanced

Not implemented