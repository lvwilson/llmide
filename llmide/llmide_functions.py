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

def get_default_shell():
    """Returns the default shell for the current user."""
    if sys.platform == "win32":
        # Default to cmd.exe on Windows, as detailed shell detection is complex
        return os.getenv('COMSPEC', 'cmd.exe')
    else:
        # Get the default shell from the user's entry in the password database on Unix-like systems
        return pwd.getpwuid(os.getuid()).pw_shell
    
def find_and_replace(file_path, command):
    try:
        with open(file_path, "r") as file:
            source_code = file.read()
    except Exception as e:
        return (file_path + " read error: " + str(e))
    source_code = findreplace.find_replace(source_code, command)
    try:
        with open(file_path, "w") as file:
            file.write(source_code)
        return (file_path + " successfully written.")
    except Exception as e:
        return (file_path + " write error: " + str(e))

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

def write_text_to_file(file_path, code):
    """
    Write the given code to a file specified by file_path. Use this when creating a new file.

    Parameters:
    code (str): The code to write.
    file_path (str): The path of the file to write to.

    Returns:
    str: A message indicating whether the file was successfully written or an error occurred.
    """
    try:
        with open(file_path, "w") as file:
            file.write(code)
        return (file_path + " successfully written.")
    except Exception as e:
        return (file_path + " write error: " + str(e))

def read_text_from_file(file_path):
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
