import re
from . import llmide_functions

def split_preserving_quotes(s):
    # This regex will split by spaces but preserve quoted segments
    pattern = r'(?:"[^"]*"|\'[^\']*\'|\S)+'
    matches = re.findall(pattern, s)
    
    # Remove the quotes from the matches
    result = [match[1:-1] if match[0] in ('"', "'") else match for match in matches]
    return result

# Example usage
#input_string = 'This is a "quoted segment" and this is \'another one\''
#split_result = split_preserving_quotes(input_string)
#print(split_result)


def process_content(content):
    # Regex pattern to find the command and arguments
    command_pattern = r"^Command: (\S+)\s*(.*)$"
    # Updated regex pattern to ignore the language specifier in the opening backticks
    backtick_pattern = r"```(?:\w+)?\s*(.*?)```"
    
    # Searching for the command and arguments
    command_match = re.search(command_pattern, content, re.MULTILINE)
    if command_match:
        command = command_match.group(1)
        arguments = command_match.group(2)
    else:
        command = None
        arguments = None
    
    # Searching for content within backticks
    backtick_match = None
    backtick_matches = re.findall(backtick_pattern, content, re.DOTALL)
    #print(backtick_matches[0])
    if len(backtick_matches) > 0:
        backtick_match = backtick_matches[0]
    if backtick_match:
        backtick_content = backtick_match
    else:
        backtick_content = None
    if command:
        if command.lower() in ["none", "none.", "done.", "finished.", "done", "finished"]:
            return "End."
        return _execute_command(command, arguments, backtick_content)
    else:
        return "End."

def _execute_command(command, arguments, backticks):
    if command is None:
        return "Error: Command name must be specified correctly."
    if command != "run_console_command":
        args = split_preserving_quotes(arguments)
    else:
        args = arguments
    if not isinstance(args, list):
        args = [args]
    if backticks is not None:
        args.append(backticks)
    if not args:
        return "Error: Arguments must be specified correctly"
    try:
        function = getattr(llmide_functions, command.lower())
    except AttributeError:
        return "Error: Command not found"
    try:
        return function(*args)
    except Exception as e:
        return f"Error executing command: {e}"

# Example usage:
# content = """
# Random content...
# Command: test_function arg1 arg2
# ```Python
# stuff in here
# and more stuff
# ```
# """

# content = """
# Detailed thoughts and Plans: 
# First, I will read the code from the file `test.py` to understand its structure and identify any potential issues. Once I have the code, I will inspect it for any syntax errors, logic errors, or other issues that may need debugging.

# Command: read_code_from_file test.py
# """

#print(process_content(content))

# content = """
# Detailed thoughts and Plans: 
# I will run the tree command to understand the directory structure of the project

# Command: run_console_command tree
# """
# process_content(content)
