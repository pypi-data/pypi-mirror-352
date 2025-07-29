"""
Basic tests for docstring-composer.
"""

import json
import unittest
from typing import Dict, Any

from docstring_composer.composer import DocstringComposer
from docstring_composer.schema import load_schema


class TestDocstringComposer(unittest.TestCase):
    """
    Test cases for the DocstringComposer class.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.composer = DocstringComposer()
        
        # Create a simple schema for testing
        self.test_schema: Dict[str, Any] = {
            "name": "test_function",
            "short_description": "A test function to demonstrate docstring formatting.",
            "long_description": "This function is used in unit tests to verify that the docstring formatters work correctly.",
            "parameters": [
                {
                    "name": "param1",
                    "type": "str",
                    "description": "The first parameter.",
                    "required": True
                },
                {
                    "name": "param2",
                    "type": "int",
                    "description": "The second parameter.",
                    "default": 0,
                    "required": False
                }
            ],
            "returns": {
                "type": "bool",
                "description": "True if successful, False otherwise."
            },
            "raises": [
                {
                    "exception": "ValueError",
                    "description": "If param1 is empty."
                }
            ],
            "examples": [
                {
                    "code": "result = test_function('example', 42)\nprint(result)",
                    "description": "A simple example of how to use the function."
                }
            ],
            "notes": "This is just a test function and doesn't do anything useful."
        }

    def test_python_google_formatter(self):
        """
        Test the Python Google-style formatter.
        """
        result = self.composer.convert(
            schema=self.test_schema, 
            language="python", 
            style="google"
        )
        
        self.assertIn("A test function to demonstrate", result)
        self.assertIn("Args:", result)
        self.assertIn("param1 (str):", result)
        self.assertIn("Returns:", result)
        self.assertIn("bool:", result)
        self.assertIn("Raises:", result)
        self.assertIn("ValueError:", result)
        self.assertIn("Examples:", result)
        self.assertIn("result = test_function(", result)

    def test_python_numpy_formatter(self):
        """
        Test the Python NumPy-style formatter.
        """
        result = self.composer.convert(
            schema=self.test_schema, 
            language="python", 
            style="numpy"
        )
        
        self.assertIn("A test function to demonstrate", result)
        self.assertIn("Parameters", result)
        self.assertIn("----------", result)
        self.assertIn("param1 : str", result)
        self.assertIn("Returns", result)
        self.assertIn("-------", result)
        self.assertIn("bool", result)
        self.assertIn("Raises", result)
        self.assertIn("------", result)
        self.assertIn("ValueError", result)
        
    def test_python_epydoc_formatter(self):
        """
        Test the Python Epydoc-style formatter.
        """
        result = self.composer.convert(
            schema=self.test_schema, 
            language="python", 
            style="epydoc"
        )
        
        self.assertIn("A test function to demonstrate", result)
        self.assertIn("@param param1:", result)
        self.assertIn("@type param1: str", result)
        self.assertIn("@return:", result)
        self.assertIn("@rtype: bool", result)
        self.assertIn("@raise ValueError:", result)
        self.assertIn("Examples:", result)
        self.assertIn("@example:", result)
        self.assertIn("@note:", result)
        self.assertIn("This is just a test function", result)

    def test_python_rest_formatter(self):
        """
        Test the Python reStructuredText (reST)-style formatter.
        """
        result = self.composer.convert(
            schema=self.test_schema, 
            language="python", 
            style="rest"
        )
        
        self.assertIn("A test function to demonstrate", result)
        self.assertIn(":Parameters:", result)
        self.assertIn("**param1** : str", result)
        self.assertIn(":Returns:", result)
        self.assertIn("**bool**", result)
        self.assertIn(":Raises:", result)
        self.assertIn("**ValueError**", result)
        self.assertIn(":Examples:", result)
        self.assertIn(".. code-block:: python", result)
        self.assertIn(":Notes:", result)
        self.assertIn("This is just a test function", result)

    def test_java_javadoc_formatter(self):
        """
        Test the Java Javadoc formatter.
        """
        result = self.composer.convert(
            schema=self.test_schema, 
            language="java", 
            style="javadoc"
        )
        
        self.assertIn("/**", result)
        self.assertIn(" * A test function to demonstrate", result)
        self.assertIn(" * @param param1", result)
        self.assertIn(" * @return", result)
        self.assertIn(" * @throws ValueError", result)
        self.assertIn(" */", result)

    def test_js_jsdoc_formatter(self):
        """
        Test the JavaScript JSDoc formatter.
        """
        result = self.composer.convert(
            schema=self.test_schema, 
            language="javascript", 
            style="jsdoc"
        )
        
        self.assertIn("/**", result)
        self.assertIn(" * A test function to demonstrate", result)
        self.assertIn(" * @param {str} param1", result)
        self.assertIn(" * @returns {bool}", result)
        self.assertIn(" * @throws {ValueError}", result)
        self.assertIn(" */", result)

    def test_kotlin_kdoc_formatter(self):
        """
        Test the Kotlin KDoc formatter.
        """
        result = self.composer.convert(
            schema=self.test_schema, 
            language="kotlin", 
            style="kdoc"
        )
        
        self.assertIn("/**", result)
        self.assertIn(" * A test function to demonstrate", result)
        self.assertIn(" * @param param1", result)
        self.assertIn(" * @return", result)
        self.assertIn(" * @throws ValueError", result)
        self.assertIn(" */", result)

    def test_c_doxygen_formatter(self):
        """
        Test the C Doxygen formatter.
        """
        result = self.composer.convert(
            schema=self.test_schema, 
            language="c", 
            style="doxygen"
        )
        
        self.assertIn("/**", result)
        self.assertIn(" * @brief A test function to demonstrate", result)
        self.assertIn(" * @param[in] param1", result)
        self.assertIn(" * @return", result)
        self.assertIn(" * @exception", result)
        self.assertIn(" */", result)

    def test_cpp_doxygen_formatter(self):
        """
        Test the C++ Doxygen formatter.
        """
        result = self.composer.convert(
            schema=self.test_schema, 
            language="cpp", 
            style="doxygen"
        )
        
        self.assertIn("/**", result)
        self.assertIn(" * @brief A test function to demonstrate", result)
        self.assertIn(" * @param param1", result)
        self.assertIn(" * @return", result)
        self.assertIn(" * @throw", result)
        self.assertIn(" */", result)

    def test_php_phpdoc_formatter(self):
        """
        Test the PHP PHPDoc formatter.
        """
        result = self.composer.convert(
            schema=self.test_schema, 
            language="php", 
            style="phpdoc"
        )
        
        self.assertIn("/**", result)
        self.assertIn(" * A test function to demonstrate", result)
        self.assertIn(" * @param str $param1", result)
        self.assertIn(" * @return bool", result)
        self.assertIn(" * @throws ValueError", result)
        self.assertIn(" */", result)

    def test_go_godoc_formatter(self):
        """
        Test the Go GoDoc formatter.
        """
        result = self.composer.convert(
            schema=self.test_schema, 
            language="go", 
            style="godoc"
        )
        
        self.assertIn("// ", result)  # Go comments start with //
        self.assertIn("// Test_function A test function", result)
        self.assertIn("// param1:", result)
        self.assertIn("// Returns:", result)
        self.assertIn("// Errors:", result)


if __name__ == "__main__":
    unittest.main()
