import re
import llmide

def parse_content(content):
    # Regex pattern to find the command and arguments
    command_pattern = r"^Command:(\S+)\s*(.*)$"
    # Updated regex pattern to ignore the language specifier in the opening backticks
    backtick_pattern = r"```(?:\w+)?\s*(.*?)(?=```)"
    
    # Searching for the command and arguments
    command_match = re.search(command_pattern, content, re.MULTILINE)
    if command_match:
        command = command_match.group(1)
        arguments = command_match.group(2)
    else:
        command = None
        arguments = None
    
    # Searching for content within backticks
    backtick_match = re.search(backtick_pattern, content, re.DOTALL)
    if backtick_match:
        backtick_content = backtick_match.group(1).strip()
    else:
        backtick_content = None
    
    return {
        'command': command,
        'arguments': arguments,
        'backtick_content': backtick_content
    }

# Example usage:
content = """
Random content...
Command:test_function arg1
```Python
stuff in here
and more stuff
```
"""

result = parse_content(content)
function = getattr(llmide, result['command'])
function(result['backtick_content'], result['arguments'])
#print("Command:", result['command'])
#print("Arguments:", result['arguments'])
#print("Content in backticks:", result['backtick_content'])
