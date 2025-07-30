# Docstring Composer

A Python package that converts schema-based docstrings to different language formats, including:

- Google-style docstrings for Python
- Javadoc for Java
- JSDoc for JavaScript/TypeScript
- And more...

## Installation

```bash
pip install docstring-composer
```

## Usage

### Command Line

```bash
# Convert a docstring schema file to a specific language format
docstring-composer convert --schema input.json --language python --style google --output output.py

# or pipe from stdin
cat input.json | docstring-composer convert --language java
```

### Python API

```python
from docstring_composer import DocstringComposer

# Create a composer instance
composer = DocstringComposer()

# Convert a docstring schema to a specific language format
docstring_schema = {...}  # Your docstring schema as a dictionary
result = composer.convert(
    schema=docstring_schema, 
    language="python", 
    style="google"
)
print(result)
```

## Supported Languages and Styles

- Python: "google", "numpy", "sphinx", "epydoc", "rest"
- Java: "javadoc"
- JavaScript/TypeScript: "jsdoc", "typedoc"
- C#: "xmldoc"
- Ruby: "yard"
- Kotlin: "kdoc"
- C: "doxygen"
- C++: "doxygen"
- PHP: "phpdoc"
- Go: "godoc"

## License

MIT License
