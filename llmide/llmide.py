import re
from collections import namedtuple
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


def process_slice(content):
    # Regex pattern to find the command and arguments
    command_pattern = r"^Command: (\S+)\s*(.*)$"
    # Updated regex pattern to ignore the language specifier in the opening backticks
    #backtick_pattern = r"`````(?:\w+)?\s*(.*?)`````"
    # Updated to catch special characters
    backtick_pattern = r"`````(?:[\w#\+\-]+)?\s*(.*?)`````"
    
    # Searching for the command and arguments
    command_match = re.search(command_pattern, content, re.MULTILINE)
    if command_match:
        command = command_match.group(1)
        arguments = command_match.group(2)
        command_end_pos = command_match.end()
    else:
        command = None
        arguments = None
        command_end_pos = -1
    
    # Searching for content within backticks
    backtick_match = None
    backtick_match = re.search(backtick_pattern, content, re.DOTALL)
    if backtick_match:
        backtick_content = backtick_match.group(1)
        backtick_start_pos = backtick_match.start()
        backtick_end_pos = backtick_match.end()
    else:
        backtick_content = None
        backtick_end_pos = -1
        backtick_start_pos = -1

    #ignore backticks if not directly attached to command
    if (backtick_start_pos - command_end_pos > 1):
        backtick_content = None
        backtick_end_pos = -1

    split_position = max(command_end_pos, backtick_end_pos)
    remaining_content = content[split_position:].strip()
    if command:
        return command, arguments, backtick_content, remaining_content
    else:
        return None, None, None, None

CommandInfo = namedtuple('CommandInfo', ['command', 'arguments', 'backtick_content'])

def concise_representation(input_string, max_chars):
    if len(input_string) <= max_chars:
        return input_string

    # Calculate how much of the string we can show at the start and end
    part_length = (max_chars - 3) // 2  # Deduct 3 for the ellipses
    first_part = input_string[:part_length]
    last_part = input_string[-part_length:] if (max_chars % 2 == 0) else input_string[-(part_length + 1):]

    return f"{first_part}...{last_part}"


#cut the output at the final read command or first non read command after a read command
def filter_content(content):
    read_command_encountered = False
    command, arguments, backtick_content, remaining_content = process_slice(content)
    if command:
        command = CommandInfo(command, arguments, backtick_content)
        if command =='read_file':
            read_command_encountered = True
    previous_remaining_content = remaining_content
    while command:
        command, arguments, backtick_content, remaining_content = process_slice(remaining_content)
        if command:
            if command =='read_file':
                read_command_encountered = True
            elif read_command_encountered:
                n_to_copy = len(content) - len(previous_remaining_content)
                return content[:n_to_copy]#clip here
            previous_remaining_content = remaining_content
    return content

def process_content(content):
    commands = []
    command, arguments, backtick_content, remaining_content = process_slice(content)
    if command:
        commands.append(CommandInfo(command, arguments, backtick_content))
    #append all of the above to the structure properly
    while command:
        command, arguments, backtick_content, remaining_content = process_slice(remaining_content)
        if command:
            commands.append(CommandInfo(command, arguments, backtick_content))
        #append all of the above to the structure properly
    response = ""
    if len(commands) == 0:
        return "End."
    for command in commands:
        command_response = _execute_command(command.command, command.arguments, command.backtick_content) + "\n"
        if command.command == "run_console_command":            
            limit = 10000
            if len(command_response) >= limit:
                concise_command_response = concise_representation (command_response, limit)
                command_response = f"Truncating command response to {limit} characters...\n"+concise_command_response
                print (command_response)
        response += command_response
    return response
    

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
        return f"Error executing command: {e}\n {command}, {arguments}, {backticks}"

def terminate_process():
    llmide_functions.terminate_process()
# Example usage:
# content = """
# Random content...
# Command: test_function arg1 arg2
# `````Python
# stuff in here
# and more stuff
# `````
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
