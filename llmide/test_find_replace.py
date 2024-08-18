import unittest
import re
from findreplace import find_replace

def load_source_code(file_path):
    with open(file_path, 'r') as file:
        return file.read()

class TestFindReplace(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the advanced_playground.py file once for all tests
        cls.source_code = load_source_code('sample_code.py')
        print("Loaded Source Code:\n", cls.source_code)  # Debug line to check the loaded content

    def test_simple_replacement_in_class_method(self):
        command = """<<<<<<< SEARCH
    def start_engine(self):
        print(f"{self.brand} {self.model} engine started.")
=======
    def start_engine(self):
        print(f"{self.brand} {self.model} roars to life!")
>>>>>>> REPLACE"""
        expected_output_contains = "print(f\"{self.brand} {self.model} roars to life!\")"
        result = find_replace(self.source_code, command)
        self.assertIn(expected_output_contains, result)

    def test_replace_nested_function_in_decorated_function(self):
        command = """<<<<<<< SEARCH
    def inner_calculation(y):
        return x * y + (lambda z: z**2)(y)
=======
    def inner_calculation(y):
        return x * y + (lambda z: z**3)(y)
>>>>>>> REPLACE"""
        expected_output_contains = "return x * y + (lambda z: z**3)(y)"
        result = find_replace(self.source_code, command)
        self.assertIn(expected_output_contains, result)

    def test_replace_class_variable_in_nested_class(self):
        command = """<<<<<<< SEARCH
        self.value = value
=======
        self.value = value * 2
>>>>>>> REPLACE"""
        expected_output_contains = "self.value = value * 2"
        result = find_replace(self.source_code, command)
        self.assertIn(expected_output_contains, result)

    def test_replace_function_with_multiple_decorators(self):
        command = """<<<<<<< SEARCH
def complex_calculation(x):
=======
def complex_calculation(x):
    print(f"Starting complex calculation with x={x}")
>>>>>>> REPLACE"""
        expected_output_contains = "print(f\"Starting complex calculation with x={x}\")"
        result = find_replace(self.source_code, command)
        self.assertIn(expected_output_contains, result)

if __name__ == "__main__":
    unittest.main()


def load_source_code(file_path):
    with open(file_path, 'r') as file:
        return file.read()

class TestFindReplace(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the advanced_playground.py file once for all tests
        cls.source_code = load_source_code('test_code.py')

    def test_simple_replacement_in_class_method(self):
        command = """<<<<<<< SEARCH
    def start_engine(self):
        print(f"{self.brand} {self.model} engine started.")
=======
    def start_engine(self):
        print(f"{self.brand} {self.model} roars to life!")
>>>>>>> REPLACE"""
        expected_output_contains = "print(f\"{self.brand} {self.model} roars to life!\")"
        result = find_replace(self.source_code, command)
        self.assertIn(expected_output_contains, result)

    def test_replace_nested_function_in_decorated_function(self):
        command = """<<<<<<< SEARCH
    def inner_calculation(y):
        return x * y + (lambda z: z**2)(y)
=======
    def inner_calculation(y):
        return x * y + (lambda z: z**3)(y)
>>>>>>> REPLACE"""
        expected_output_contains = "return x * y + (lambda z: z**3)(y)"
        result = find_replace(self.source_code, command)
        self.assertIn(expected_output_contains, result)

    def test_replace_class_variable_in_nested_class(self):
        command = """<<<<<<< SEARCH
        self.value = value
=======
        self.value = value * 2
>>>>>>> REPLACE"""
        expected_output_contains = "self.value = value * 2"
        result = find_replace(self.source_code, command)
        self.assertIn(expected_output_contains, result)

    def test_replace_function_with_multiple_decorators(self):
        command = """<<<<<<< SEARCH
def complex_calculation(x):
=======
def complex_calculation(x):
    print(f"Starting complex calculation with x={x}")
>>>>>>> REPLACE"""
        expected_output_contains = "print(f\"Starting complex calculation with x={x}\")"
        result = find_replace(self.source_code, command)
        self.assertIn(expected_output_contains, result)

if __name__ == "__main__":
    unittest.main()
