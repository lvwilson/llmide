from . import codemanipulator
import os
import signal
import io
import pty
import subprocess
import threading
import sys
from . import code_scissors
import pwd
from . import findreplace
import difflib

_backticks = '`````'

def get_default_shell():
    """Returns the default shell for the current user."""
    if sys.platform == "win32":
        # Default to cmd.exe on Windows, as detailed shell detection is complex
        return os.getenv('COMSPEC', 'cmd.exe')
    else:
        # Get the default shell from the user's entry in the password database on Unix-like systems
        return pwd.getpwuid(os.getuid()).pw_shell
    
def find_and_replace(file_path, command):
    """
    Perform a find and replace operation on a file and return the diff.

    Parameters:
    file_path (str): Path to the file to modify.
    command: The find-replace command to execute (handled by `findreplace.find_replace`).

    Returns:
    str: A message indicating the success of the operation, or any error encountered,
         along with the diff of changes made.
    """
    try:
        with open(file_path, "r") as file:
            original_content = file.read()
    except Exception as e:
        return (file_path + " read error: " + str(e))

    # Perform the find and replace operation
    modified_content = findreplace.find_replace(original_content, command)

    # Generate the diff
    diff = "\n".join(difflib.unified_diff(
        original_content.splitlines(),
        modified_content.splitlines(),
        lineterm="",
        fromfile="original",
        tofile="modified"
    ))

    try:
        with open(file_path, "w") as file:
            file.write(modified_content)
        return (f"{file_path} successfully written.\n\nDiff:\n{diff}")
    except Exception as e:
        return (file_path + " write error: " + str(e))

# def find_and_replace(file_path, command):
#     try:
#         with open(file_path, "r") as file:
#             source_code = file.read()
#     except Exception as e:
#         return (file_path + " read error: " + str(e))
#     source_code = findreplace.find_replace(source_code, command)
#     try:
#         with open(file_path, "w") as file:
#             file.write(source_code)
#         return (file_path + " successfully written.")
#     except Exception as e:
#         return (file_path + " write error: " + str(e))

def insert_text_after_matching_line(file_path, line, new_code):
    try:
        with open(file_path, "r") as file:
            source_code = file.read()
    except Exception as e:
        return (file_path + " read error: " + str(e))
    source_code = code_scissors.insert_after(source_code, line, new_code)
    try:
        with open(file_path, "w") as file:
            file.write(source_code)
        return (file_path + " successfully written.")
    except Exception as e:
        return (file_path + " write error: " + str(e))
    
def insert_text_before_matching_line(file_path, line, new_code):
    try:
        with open(file_path, "r") as file:
            source_code = file.read()
    except Exception as e:
        return (file_path + " read error: " + str(e))
    source_code = code_scissors.insert_before(source_code, line, new_code)
    try:
        with open(file_path, "w") as file:
            file.write(source_code)
        return (file_path + " successfully written.")
    except Exception as e:
        return (file_path + " write error: " + str(e))
    
def replace_text_before_matching_line(file_path, line, new_code):
    try:
        with open(file_path, "r") as file:
            source_code = file.read()
    except Exception as e:
        return (file_path + " read error: " + str(e))
    source_code = code_scissors.replace_before(source_code, line, new_code)
    try:
        with open(file_path, "w") as file:
            file.write(source_code)
        return (file_path + " successfully written.")
    except Exception as e:
        return (file_path + " write error: " + str(e))
    
def replace_text_after_matching_line(file_path, line, new_code):
    try:
        with open(file_path, "r") as file:
            source_code = file.read()
    except Exception as e:
        return (file_path + " read error: " + str(e))
    source_code = code_scissors.replace_after(source_code, line, new_code)
    try:
        with open(file_path, "w") as file:
            file.write(source_code)
        return (file_path + " successfully written.")
    except Exception as e:
        return (file_path + " write error: " + str(e))
    
def replace_text_between_matching_lines(file_path, line1, line2, new_code):
    try:
        with open(file_path, "r") as file:
            source_code = file.read()
    except Exception as e:
        return (file_path + " read error: " + str(e))
    source_code = code_scissors.replace_between(source_code, line1, line2, new_code)
    try:
        with open(file_path, "w") as file:
            file.write(source_code)
        return (file_path + " successfully written.")
    except Exception as e:
        return (file_path + " write error: " + str(e))

def read_code_signatures_and_docstrings(file_path):
    """
    Read the code signatures and docstrings of a file to get a basic understanding of the structure of the code.

    Parameters:
    file_path (str): The path to the source code file.

    Returns:
    str: The signatures and docstrings of the functions and classes in the file, or an error message if reading the file fails.
    """
    try:
        with open(file_path, "r") as file:
            source_code = file.read()
            return codemanipulator.get_signatures_and_docstrings(source_code)
    except Exception as e:
        return (file_path + " read error: " + str(e))

def replace_docstring_at_address(file_path, address, new_docstring):
    """
    Replace the docstring in a source code file at a specific address with the provided docstring.

    Parameters:
    file_path (str): The path to the source code file.
    address (str): A dot-separated path indicating the location of the target node. The address can point to a top-level function or class ("FunctionName"), a method within a class ("ClassName.method_name"), or elements within nested classes ("OuterClass.InnerClass.method_name").
    new_docstring (str): The new docstring to write to the file in the specified location.

    Returns:
    str: A message indicating whether the operation was successful or an error occurred.
    """
    try:
        with open(file_path, "r") as file:
            source_code = file.read()
    except Exception as e:
        return (file_path + " read error: " + str(e))
    source_code = codemanipulator.change_docstring(source_code, address, new_docstring)
    try:
        return codemanipulator.write_code(file_path, source_code)
    except Exception as e:
        return (file_path + " write error: " + str(e))

def read_code_at_address(file_path, address):
    """
    Retrieve the source code at a specific address within the provided source code file.

    Parameters:
    file_path (str): The path to the source code file.
    address (str): A dot-separated path indicating the location of the target node. The address can point to a top-level function or class ("FunctionName"), a method within a class ("ClassName.method_name"), or elements within nested classes ("OuterClass.InnerClass.method_name").

    Returns:
    str: The source code at the specified address, or a message if not found or an error occurred.
    """
    try:
        with open(file_path, "r") as file:
            source_code = file.read()
            return codemanipulator.read_code_at_address(source_code, address)
    except Exception as e:
        return (file_path + " read error: " + str(e))

def replace_code_at_address(file_path, address, new_code):
    """
    Replace the code at a specific address within the provided source code file with the new code.

    Parameters:
    file_path (str): The path to the source code file.
    address (str): A dot-separated path indicating the location of the target node.
    new_code (str): The new code to replace the existing code.

    Returns:
    str: A message indicating whether the operation was successful or an error occurred.
    """
    source_code = ""
    try:
        with open(file_path, "r") as file:
            source_code = file.read()
    except Exception as e:
        return (file_path + " read error: " + str(e))
    try:
        source_code = codemanipulator.replace_code(source_code, address, new_code)
    except Exception as e:
        return (file_path + " replace error: " + str(e))
    try:
        return codemanipulator.write_code(file_path, source_code)
    except Exception as e:
        return (file_path + " write error: " + str(e))

def add_code_after_address(file_path, address, new_code):
    """
    Add new code after a specific address within the provided source code file.

    Parameters:
    file_path (str): The path to the source code file.
    address (str): A dot-separated path indicating the location of the target node.
    new_code (str): The new code to add after the specified address.

    Returns:
    str: A message indicating whether the operation was successful or an error occurred.
    """
    try:
        with open(file_path, "r") as file:
            source_code = file.read()
    except Exception as e:
        return (file_path + " read error: " + str(e))
    source_code = codemanipulator.insert_code_after(source_code, address, new_code)
    try:
        with open(file_path, "w") as file:
            file.write(source_code)
        return (file_path + " successfully written.")
    except Exception as e:
        return (file_path + " write error: " + str(e))

def add_code_before_address(file_path, address, new_code):
    """
    Add new code before a specific address within the provided source code file.

    Parameters:
    file_path (str): The path to the source code file.
    address (str): A dot-separated path indicating the location of the target node.
    new_code (str): The new code to add before the specified address.

    Returns:
    str: A message indicating whether the operation was successful or an error occurred.
    """
    try:
        with open(file_path, "r") as file:
            source_code = file.read()
    except Exception as e:
        return (file_path + " read error: " + str(e))
    source_code = codemanipulator.insert_code_before(source_code, address, new_code)
    try:
        with open(file_path, "w") as file:
            file.write(source_code)
        return (file_path + " successfully written.")
    except Exception as e:
        return (file_path + " write error: " + str(e))
    
def remove_code_at_address(file_path, address):
    """
    Removes code at a specific address within the provided source code file.

    Parameters:
    file_path (str): The path to the source code file.
    address (str): A dot-separated path indicating the location of the target node.

    Returns:
    str: A message indicating whether the operation was successful or an error occurred.
    """
    try:
        with open(file_path, "r") as file:
            source_code = file.read()
    except Exception as e:
        return (file_path + " read error: " + str(e))
    source_code = codemanipulator.remove_code(source_code, address)
    try:
        with open(file_path, "w") as file:
            file.write(source_code)
        return (file_path + " successfully written.")
    except Exception as e:
        return (file_path + " write error: " + str(e))


def manipulate_file_agent(file_path, instructions):

    client = claudeclient.AIClient()

    def extract_contents(output):
        # Define the pattern to match each section
        pattern = r"(?P<section>[\w\s/]+?)\s`````(.*?)`````"
        
        # Use regex to find all sections
        matches = re.findall(pattern, output, re.DOTALL)
        
        # Create a dictionary from matches with stripped values or None if empty
        sections = {match[0].strip(): match[1].strip() if match[1].strip() else None for match in matches}
        
        # Map specific sections to desired keys (case-sensitive)
        thoughts = sections.get('Thoughts', None)
        feedback = sections.get('Feedback', None)
        file_contents = sections.get('path/to/file', None)  # Preserve case for 'path/to/file'
        
        return thoughts, feedback, file_contents

    system_prompt = """
You are a highly specialized agent tasked with manipulating code and text files. Your role is to faithfully execute the provided instructions on the given input file and output the modified file. Your behavior is guided by the following principles:

1. **Instruction Fidelity**: 
   - Execute the provided instructions exactly as stated when they are provided. Do not deviate, interpret, or infer intentions beyond what is explicitly given.
   - If the instructions include verbatim code, ensure it is inserted or modified exactly as written, exactly where it is intended.
   - If there is insufficient context to understand intent do not output the file and provide feedback to the calling system.

2. **Precision and Clarity**:
   - If an instruction is ambiguous or could lead to multiple valid outputs, choose the most straightforward interpretation and document any assumptions within comments, but only if allowed.
   - Do not include extraneous changes, explanations, or modifications outside the scope of the instructions.

3. **File Integrity**:
   - Ensure that the output preserves the original structure and formatting of the file unless explicitly instructed otherwise.
   - Retain all original content that is not affected by the instructions.

4. **Error Handling**:
   - If the instructions cannot be implemented due to conflicts, missing details, or contradictions, output the original file unchanged and document the issue (if permitted by the task).

5. **Neutrality**:
   - Avoid injecting personal style, optimizations, or corrections unless explicitly requested. Your focus is solely on fulfilling the instructions as provided.

### Input structure:
Specific changes to apply to the file, which may include verbatim code, descriptions, or general guidance. 
path/to/file `````The unmodified code or text file.`````

### Output structure:
Thoughts `````An optional area for you to think through the changes if needed and record your thoughts````
Feedback `````Your feedback if any to the calling agent. This should be blank unless you absolutely require more information to complete the task.`````
path/to/file `````The whole and complete modified file with the changes applied as per the instructions, without adding, omitting, or altering anything outside the scope.`````

**Feedback and file output are mutually exclusive, if feedback is provided the file will not be written, so in the case where feedback is required do not output the file contents.**

**Always prioritize exactness and consistency with the instructions above.**
"""
    context = []

    try:
        with open(file_path, "r") as file:
            original_contents = file.read()
            original_length = len(original_contents)
            if (original_length) >= 300000:
                return (file_path + " read error: the file is too large for the agent to manipulate. Stop work and report." + str(e)) 
    except Exception as e:
        return (file_path + " read error: " + str(e))

    
    formatted_content = f"{file_path} {_backticks}{original_contents}{_backticks}"
    
    context.append(AIClient.form_message("user", formatted_content))

    #create response
    response = self.client.generate_response(system_prompt, context)

    thoughts, feedback, new_contents = extract_contents(response)

    if feedback is not None:
        return feedback + "\nFile not written."

    if new_contents is None:
        return "File manipulation agent provided unexpected output. File not written."

    # Generate the diff between the original and new content
    diff = "\n".join(difflib.unified_diff(
        original_contents.splitlines(),
        new_contents.splitlines(),
        lineterm="",
        fromfile="original",
        tofile="new"
    ))

    try:# 
        with open(file_path, "w") as file:
            file.write(new_contents)
            return (f"{file_path} successfully written.")
    except Exception as e:
        return (file_path + " write error: " + str(e))

def append_to_file(file_path, log_message):
    """
    Append the given log message to a file specified by file_path.
    Outputs the lengths of the original and new file contents, as well as the diff.

    Parameters:
    log_message (str): The log message to append.
    file_path (str): The path of the file to append to.

    Returns:
    str: A message indicating the success of the operation, 
         lengths of original and new contents, the diff, or any error encountered.
    """
    import difflib

    original_content = ""
    original_length = 0
    new_length = 0

    try:
        # Check if the file exists and read its contents to get the original length
        try:
            with open(file_path, "r") as file:
                original_content = file.read()
                original_length = len(original_content)
        except FileNotFoundError:
            original_content = ""  # File does not exist, so original content is empty
            original_length = 0

        # Append the new log message to the file
        with open(file_path, "a") as file:
            file.write(log_message + "\n")

        # Read the updated file to determine the new length
        with open(file_path, "r") as file:
            updated_content = file.read()
            new_length = len(updated_content)

        # Generate the diff between the original and updated content
        diff = "\n".join(difflib.unified_diff(
            original_content.splitlines(),
            updated_content.splitlines(),
            lineterm="",
            fromfile="original",
            tofile="updated"
        ))

        return (f"{file_path} successfully appended. Original length: {original_length}, "
                f"New length: {new_length}.\n\nDiff:\n{diff}")

    except Exception as e:
        return (file_path + " append error: " + str(e))

def write_file(file_path, code):
    """
    Write the given code to a file specified by file_path.
    Outputs the lengths of the original and new file contents, as well as the diff.

    Parameters:
    code (str): The code to write.
    file_path (str): The path of the file to write to.

    Returns:
    str: A message indicating the success of the operation, 
         lengths of original and new contents, the diff, or any error encountered.
    """
    original_content = ""
    original_length = 0
    new_length = len(code)

    try:
        # Check if the file exists and read its contents to get the original length
        try:
            with open(file_path, "r") as file:
                original_content = file.read()
                original_length = len(original_content)
        except FileNotFoundError:
            original_content = ""  # File does not exist, so original content is empty
            original_length = 0

        # Generate the diff between the original and new content
        diff = "\n".join(difflib.unified_diff(
            original_content.splitlines(),
            code.splitlines(),
            lineterm="",
            fromfile="original",
            tofile="new"
        ))

        # Write the new content to the file
        with open(file_path, "w") as file:
            file.write(code)

        return (f"{file_path} successfully written. Original length: {original_length}, "
                f"New length: {new_length}.\n\nDiff:\n{diff}")

    except Exception as e:
        return (file_path + " write error: " + str(e))

# def write_file(file_path, code):
#     """
#     Write the given code to a file specified by file_path. 
#     Outputs the lengths of the original and new file contents.

#     Parameters:
#     code (str): The code to write.
#     file_path (str): The path of the file to write to.

#     Returns:
#     str: A message indicating the success of the operation, 
#          lengths of original and new contents, or any error encountered.
#     """
#     original_length = 0
#     new_length = len(code)

#     try:
#         # Check if the file exists and read its contents to get the original length
#         try:
#             with open(file_path, "r") as file:
#                 original_content = file.read()
#                 original_length = len(original_content)
#         except FileNotFoundError:
#             original_length = 0  # File does not exist, so original length is 0
        
#         # Write the new content to the file
#         with open(file_path, "w") as file:
#             file.write(code)
        
#         return (f"{file_path} successfully written. Original length: {original_length}, "
#                 f"New length: {new_length}.")

#     except Exception as e:
#         return (file_path + " write error: " + str(e))

def read_file(file_path):
    """
    Read the entire source file specified by file_path.

    Parameters:
    file_path (str): The path of the file to read from.

    Returns:
    str: The code as a string.
    """
    with open(file_path, "r") as file:
        return file.read()
    
def terminate_process():
    global process
    if process: 
        print("Terminating process...")
        process.terminate()

# Signal handler for SIGTERM
def handle_sigterm(signum, frame):
    print ("Sigterm caught")
    terminate_process()

#register it
signal.signal(signal.SIGTERM, handle_sigterm)
    
def run_console_command(command: str) -> str:
    """
    Executes a console command using a specified shell or the system default and returns the command's output.

    :param command: A string containing the console command to be executed.
    :return: The output from the command.
    """
    global process

    def remove_surrounding_quotes(s: str) -> str:
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return s[1:-1]
        return s

    def read_output(fd, output_list):
        try:
            while True:
                data = os.read(fd, io.DEFAULT_BUFFER_SIZE).decode()
                if not data:
                    break
                sys.stdout.write(data)
                sys.stdout.flush()
                output_list.append(data)
        except OSError:
            # Handle the case where the file descriptor is closed
            pass

    try:
        output = []
        try:
            # Create a pseudo-terminal
            master_fd, slave_fd = pty.openpty()
            stripped_command = remove_surrounding_quotes(command)

            shell_path = get_default_shell()
            
            # Specify the executable shell if provided
            if shell_path:
                process = subprocess.Popen(stripped_command, shell=True, executable=shell_path, stdin=slave_fd, stdout=slave_fd, stderr=slave_fd, text=True, close_fds=True)
            else:
                process = subprocess.Popen(stripped_command, shell=True, stdin=slave_fd, stdout=slave_fd, stderr=slave_fd, text=True, close_fds=True)

            # Close the slave fd in the parent process
            os.close(slave_fd)

            # Start a thread to read the output
            output_thread = threading.Thread(target=read_output, args=(master_fd, output))
            output_thread.start()

            # Wait for the process to complete
            process.wait()
            output_thread.join()

            # Close the master fd after the thread completes
            os.close(master_fd)
        except KeyboardInterrupt:
            pass

        process = None
        # Combine the output
        combined_output = ''.join(output)
        return combined_output if combined_output else "ok"
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.stderr}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def test_function(arg, backticks):
    """
    A test function to demonstrate basic functionality.

    Parameters:
    backticks (str): A string containing backticks.
    arg (str): An argument to print.
    """
    print("test_function called")
    print("Argument:", arg)
    print("Backticks:", backticks)
