import re
import llmide_functions

def process_content(content):
    # Regex pattern to find the command and arguments
    command_pattern = r"^Command: (\S+)\s*(.*)$"
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
    if command:
        return _execute_command(command, arguments, backtick_content)
    else:
        return "End."

def _execute_command(command, arguments, backticks):
    if command is None:
        return "Error: Command name must be specified correctly."
    if arguments is None:
        arguments = []
    elif not isinstance(arguments, list):
        arguments = [arguments]
    if backticks is not None:
        arguments.append(backticks)
    if not arguments:
        return "Error: Arguments must be specified correctly"
    try:
        function = getattr(llmide_functions, command.lower())
    except AttributeError:
        return "Error: Command not found"
    try:
        return function(*arguments)
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
