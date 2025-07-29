import os
from setuptools import setup

# Copy the schema file if it exists
schema_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docstring_schema.py")
if os.path.exists(schema_file):
    import shutil
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docstring_composer", "docstring_schema.py")
    shutil.copy2(schema_file, dest)
    print(f"Copied schema file to {dest}")

# This setup.py is kept for backwards compatibility
# All configuration is now in pyproject.toml
setup()
