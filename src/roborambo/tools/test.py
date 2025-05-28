import time
import random
import json
from datetime import datetime
from .util import tool_name, tool_method, tool_class, method_arg
from .tool import Tool

@tool_class(name="Function Calling Tester", desc="A simple tool to verify that function calling is working correctly")
class TestTool(Tool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tool_method(desc='Echo back a message to verify basic function calling', enabled=True)
    @method_arg(name='message', type='str', desc='Message to echo back')
    def echo(self, message, **kwargs):
        """Simple echo to test string parameters."""
        return f"✅ Function calling works! You said: '{message}'"

    @tool_method(desc='Add two numbers together', enabled=True) 
    @method_arg(name='a', type='int', desc='First number')
    @method_arg(name='b', type='int', desc='Second number')
    def add(self, a, b, **kwargs):
        """Test numeric parameters and basic math."""
        result = a + b
        return f"✅ Math function calling works! {a} + {b} = {result}"

    @tool_method(desc='Get the current timestamp', enabled=True)
    def current_time(self, **kwargs):
        """Test functions with no parameters."""
        now = datetime.now()
        return f"✅ No-parameter function calling works! Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

    @tool_method(desc='Generate a random number within a range', enabled=True)
    @method_arg(name='min_val', type='int', desc='Minimum value (inclusive)')  
    @method_arg(name='max_val', type='int', desc='Maximum value (inclusive)')
    def random_number(self, min_val, max_val, **kwargs):
        """Test multiple parameters with validation."""
        if min_val > max_val:
            return f"❌ Error: min_val ({min_val}) cannot be greater than max_val ({max_val})"
        
        result = random.randint(min_val, max_val)
        return f"✅ Random number function calling works! Random number between {min_val} and {max_val}: {result}"

    @tool_method(desc='Perform multiple string operations on text', enabled=True)
    @method_arg(name='text', type='str', desc='Text to manipulate')
    @method_arg(name='operation', type='str', desc='Operation: uppercase, lowercase, reverse, or length')
    def string_ops(self, text, operation, **kwargs):
        """Test string parameters with validation."""
        operation = operation.lower()
        
        if operation == 'uppercase':
            result = text.upper()
            return f"✅ String manipulation works! Uppercase: '{result}'"
        elif operation == 'lowercase':
            result = text.lower()
            return f"✅ String manipulation works! Lowercase: '{result}'"
        elif operation == 'reverse':
            result = text[::-1]
            return f"✅ String manipulation works! Reversed: '{result}'"
        elif operation == 'length':
            result = len(text)
            return f"✅ String manipulation works! Length of '{text}': {result} characters"
        else:
            return f"❌ Unknown operation: '{operation}'. Try: uppercase, lowercase, reverse, or length"

    @tool_method(desc='Test boolean parameter handling', enabled=True)
    @method_arg(name='include_timestamp', type='bool', desc='Whether to include timestamp in response')
    @method_arg(name='message', type='str', desc='Message to display')
    def test_boolean(self, include_timestamp, message, **kwargs):
        """Test boolean parameters."""
        response = f"✅ Boolean function calling works! Message: '{message}'"
        
        if include_timestamp:
            timestamp = datetime.now().strftime('%H:%M:%S')
            response += f" [Time: {timestamp}]"
        
        return response

    @tool_method(desc='Test function that simulates processing time', enabled=True)
    @method_arg(name='duration', type='float', desc='How many seconds to wait (max 5 seconds)')
    def slow_function(self, duration, **kwargs):
        """Test float parameters and simulate processing."""
        # Cap duration for safety
        duration = min(float(duration), 5.0)
        
        start_time = time.time()
        time.sleep(duration)
        end_time = time.time()
        actual_duration = end_time - start_time
        
        return f"✅ Slow function calling works! Requested {duration}s, actual {actual_duration:.2f}s"

    @tool_method(desc='Test error handling in function calls', enabled=True)
    @method_arg(name='should_error', type='bool', desc='Whether this function should intentionally raise an error')
    def test_error(self, should_error, **kwargs):
        """Test error handling in function calling."""
        if should_error:
            raise ValueError("✅ Error handling works! This is an intentional test error.")
        else:
            return "✅ Error handling works! Function completed successfully without errors."

    @tool_method(desc='Show a summary of all available test functions', enabled=True)
    def test_summary(self, **kwargs):
        """Show all available test functions."""
        summary = """✅ Function Calling Test Tool Summary:

🔹 echo(message) - Test basic string parameters
🔹 add(a, b) - Test numeric parameters and math
🔹 current_time() - Test functions with no parameters  
🔹 random_number(min_val, max_val) - Test multiple numeric parameters
🔹 string_ops(text, operation) - Test string operations and validation
🔹 test_boolean(include_timestamp, message) - Test boolean parameters
🔹 slow_function(duration) - Test float parameters and processing time
🔹 test_error(should_error) - Test error handling
🔹 test_summary() - Show this summary

Try asking me to use any of these functions to verify function calling is working!"""
        
        return summary