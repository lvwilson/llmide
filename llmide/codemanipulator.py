import ast
import black

def format_code(code):
    """
    Format the given code using the Black code formatter.

    Parameters:
    code (str): The code to be formatted.

    Returns:
    str: The formatted code.
    """
    return black.format_str(code, mode=black.FileMode())

def read_code(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read()
    except Exception as e:
        raise e

def write_code(file_path, source_code):
    try:
        with open(file_path, "w") as file:
            file.write(source_code)
        return (file_path + " successfully written.")
    except Exception as e:
        raise e
    
def add_prefix_to_lines(input_string, prefix):
    lines = input_string.splitlines()
    prefixed_lines = [prefix + line for line in lines]
    result_string = '\n'.join(prefixed_lines)
    return result_string

class CodeManipulator(ast.NodeTransformer):
    def __init__(self, target, new_code=None, insert_position=None, action="replace"):
        self.target = target
        self.new_code_ast = ast.parse(new_code).body[0] if new_code else None
        self.insert_position = insert_position
        self.action = action
        self.class_stack = []
        self.found = False

    def visit_Module(self, node):
        self.generic_visit(node)
        if self.new_code_ast and "." not in self.target and self.action == "create" and not any(
            isinstance(n, ast.FunctionDef) and n.name == self.target for n in node.body):
            node.body.append(self.new_code_ast)
            self.found = True
        return node

    def visit_ClassDef(self, node):
        self.class_stack.append(node.name)
        self.generic_visit(node)
        current_path = ".".join(self.class_stack)

        if current_path == self.target:
            self.found = True
            if self.action == "replace":
                self.class_stack.pop()
                return self.new_code_ast
            elif self.action == "remove":
                self.class_stack.pop()
                return None

        if self.action == "create" and current_path == ".".join(self.target.split(".")[:-1]):
            method_name = self.target.split(".")[-1]
            if not any(isinstance(n, ast.FunctionDef) and n.name == method_name for n in node.body):
                node.body.append(self.new_code_ast)
                self.found = True

        self.class_stack.pop()
        return node

    def visit_FunctionDef(self, node):
        current_path = ".".join(self.class_stack + [node.name])

        if current_path == self.target:
            self.found = True
            if self.action == "replace":
                return self.new_code_ast if self.new_code_ast else None
            elif self.action == "remove":
                return None

        self.generic_visit(node)
        return node

    def generic_visit(self, node):
        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.AST):
                        value = self.visit(value)
                        if value is None:
                            continue
                        elif isinstance(value, list):
                            new_values.extend(value)
                        else:
                            new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node

def _create_or_replace_code(source_code, address, new_code, create_if_missing, insert_position=None, action="replace"):
    tree = ast.parse(source_code)
    manipulator = CodeManipulator(address, new_code, insert_position, action)
    modified_tree = manipulator.visit(tree)
    if not manipulator.found and not create_if_missing:
        raise ValueError(
            f"The target '{address}' does not exist and 'create_if_missing' is set to False."
        )
    modified_code = ast.unparse(modified_tree)
    return modified_code

def create_code(source_code, address, new_code):
    """
    Create new code in the source code at the specified address.

    Parameters:
    source_code (str): The source code to manipulate.
    address (str): The address of the target node.
    new_code (str): The new code to insert.

    Returns:
    str: The modified and formatted source code.
    """
    return _create_or_replace_code(source_code, address, new_code, create_if_missing=True, action="create")

def replace_code(source_code, address, new_code):
    """
    Replace existing code in the source code at the specified address.

    Parameters:
    source_code (str): The source code to manipulate.
    address (str): The address of the target node.
    new_code (str): The new code to replace the existing code.

    Returns:
    str: The modified and formatted source code.
    """
    return _create_or_replace_code(source_code, address, new_code, create_if_missing=False, action="replace")

def remove_code(source_code, address):
    """
    Remove code from the source code at the specified address.

    Parameters:
    source_code (str): The source code to manipulate.
    address (str): The address of the target node.

    Returns:
    str: The modified and formatted source code.

    Raises:
    ValueError: If the target address does not exist.
    """
    tree = ast.parse(source_code)
    manipulator = CodeManipulator(address, action="remove")
    modified_tree = manipulator.visit(tree)
    if not manipulator.found:
        raise ValueError(f"The target '{address}' does not exist.")
    modified_code = ast.unparse(modified_tree)
    return format_code(modified_code)

def insert_code_before(source_code, address, new_code):
    """
    Insert new code before the specified address in the source code.

    Parameters:
    source_code (str): The source code to manipulate.
    address (str): The address of the target node.
    new_code (str): The new code to insert.

    Returns:
    str: The modified and formatted source code.
    """
    return _create_or_replace_code(source_code, address, new_code, create_if_missing=True, insert_position='before', action="insert")

def insert_code_after(source_code, address, new_code):
    """
    Insert new code after the specified address in the source code.

    Parameters:
    source_code (str): The source code to manipulate.
    address (str): The address of the target node.
    new_code (str): The new code to insert.

    Returns:
    str: The modified and formatted source code.
    """
    return _create_or_replace_code(source_code, address, new_code, create_if_missing=True, insert_position='after', action="insert")

def get_signatures_and_docstrings(source_code):
    """
    Extract all function signatures, including regular functions, async functions, methods,
    and their associated docstrings from the given source code.

    Parameters:
    source_code (str): The source code to analyze.

    Returns:
    str: String representation of the code structure including signatures and docstrings.
    """
    tree = ast.parse(source_code)
    result_lines = []

    class SignatureVisitor(ast.NodeVisitor):
        def visit_Module(self, node):
            module_docstring = ast.get_docstring(node)
            if module_docstring:
                result_lines.append(f'"""{module_docstring}"""\n')
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            self.process_function(node, '')

        def visit_AsyncFunctionDef(self, node):
            self.process_async_function(node, '')

        def visit_ClassDef(self, node, indent=''):
            class_info = {
                'class_name': node.name,
                'docstring': ast.get_docstring(node),
                'methods': []
            }
            result_lines.append(f"{indent}class {node.name}:")
            if class_info['docstring']:
                result_lines.append(f'{indent}    """{class_info["docstring"]}"""\n')

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    self.process_function(item, indent + '    ')
                elif isinstance(item, ast.AsyncFunctionDef):
                    self.process_async_function(item, indent + '    ')
                elif isinstance(item, ast.ClassDef):
                    self.visit_ClassDef(item, indent + '    ')

        def process_function(self, node, indent):
            signature = f"{indent}def {node.name}({', '.join(arg.arg for arg in node.args.args)}):"
            docstring = ast.get_docstring(node)
            result_lines.append(signature)
            if docstring:
                out_string = f'"""{docstring}"""'
                out_string = add_prefix_to_lines(out_string, f'{indent}    ')
                result_lines.append(out_string)
            else:
                result_lines.append(f'{indent}    pass\n')

        def process_async_function(self, node, indent):
            signature = f"{indent}async def {node.name}({', '.join(arg.arg for arg in node.args.args)}):"
            docstring = ast.get_docstring(node)
            result_lines.append(signature)
            if docstring:
                out_string = f'"""{docstring}"""'
                out_string = add_prefix_to_lines(out_string, f'{indent}    ')
                result_lines.append(out_string)
            else:
                result_lines.append(f'{indent}    pass\n')

    visitor = SignatureVisitor()
    visitor.visit(tree)
    return '\n'.join(result_lines).strip()

def read_code_at_address(source_code, address):
    """
    Read and return the source code snippet at a specific address.

    Parameters:
    source_code (str): The source code to search within.
    address (str): The address of the target node in 'Class.method' or 'function' format.

    Returns:
    str: The source code at the specified address, or a message if not found.
    """
    tree = ast.parse(source_code)
    class ReadCodeVisitor(ast.NodeVisitor):
        def __init__(self):
            self.path = []
            self.code_snippet = None

        def visit_ClassDef(self, node):
            self.path.append(node.name)
            if ".".join(self.path) == address:
                self.code_snippet = ast.unparse(node)
            self.generic_visit(node)
            self.path.pop()

        def visit_FunctionDef(self, node):
            self.path.append(node.name)
            if ".".join(self.path) == address:
                self.code_snippet = ast.unparse(node)
            self.generic_visit(node)
            self.path.pop()

    visitor = ReadCodeVisitor()
    visitor.visit(tree)
    if visitor.code_snippet:
        return visitor.code_snippet
    else:
        return f"No code found at address '{address}'."
    
def change_docstring(source_code, address, new_docstring):
    """
    Change the docstring of a class or function in the source code at the specified address.

    Parameters:
    source_code (str): The source code to manipulate.
    address (str): The address of the target node.
    new_docstring (str): The new docstring to replace the existing docstring.

    Returns:
    str: The modified and formatted source code.
    """
    tree = ast.parse(source_code)

    class DocstringChanger(ast.NodeTransformer):
        def __init__(self):
            self.path = []
            self.found = False

        def visit_ClassDef(self, node):
            self.path.append(node.name)
            if ".".join(self.path) == address:
                node.body.insert(0, ast.Expr(value=ast.Constant(value=new_docstring)))
                self.found = True
            self.generic_visit(node)
            self.path.pop()
            return node

        def visit_FunctionDef(self, node):
            self.path.append(node.name)
            if ".".join(self.path) == address:
                node.body.insert(0, ast.Expr(value=ast.Constant(value=new_docstring)))
                self.found = True
            self.generic_visit(node)
            self.path.pop()
            return node

    changer = DocstringChanger()
    changer.visit(tree)
    if not changer.found:
        raise ValueError(f"The target '{address}' does not exist.")
    modified_code = ast.unparse(tree)
    return format_code(modified_code)