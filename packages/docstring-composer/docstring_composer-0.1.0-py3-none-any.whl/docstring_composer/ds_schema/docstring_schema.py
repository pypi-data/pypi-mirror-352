from pydantic import BaseModel, Field
from typing import List, Optional, Any, Literal


class DocParam(BaseModel):
    name: str = Field(..., description="Parameter name (symbol). This must match exactly as used in the function or method signature.")
    type: Optional[str] = Field(None, description="Data type of the parameter (e.g., 'str', 'int', 'float'). This is a code-level symbol.")
    description: Optional[str] = Field(None, description="Natural language explanation of the parameter's purpose.")
    default: Optional[Any] = Field(None, description="The default value for the parameter if it is optional. This is a literal or code expression.")
    required: Optional[bool] = Field(True, description="Whether the parameter is required (True) or optional (False). This is a boolean flag.")


class DocReturn(BaseModel):
    type: Optional[str] = Field(None, description="Return type as a code-level symbol (e.g., 'bool', 'List[str]').")
    description: Optional[str] = Field(None, description="Explanation in natural language of what is returned.")


class DocRaise(BaseModel):
    exception: str = Field(..., description="Name of the exception (symbol) that may be raised (e.g., 'ValueError'). Must match language syntax.")
    description: Optional[str] = Field(None, description="Condition or context in which this exception may be raised.")


class DocExample(BaseModel):
    code: str = Field(..., description="Full code block or snippet that shows how to use the documented function, method, or class. This must be valid syntax.")
    description: Optional[str] = Field(None, description="Natural language explanation of what the example demonstrates.")


class DocstringSchema(BaseModel):
    name: Optional[str] = Field(None, description="Name of the documented entity (symbol). This should exactly match the function, method, or class name in code.")

    # Descriptions
    short_description: Optional[str] = Field(
        None,
        description="One-line summary in natural language of what the function, method, or class does."
    )
    long_description: Optional[str] = Field(
        None,
        description="Extended description in natural language. Can include context, usage notes, assumptions, and inline references to symbols using consistent notation."
    )

    # Signature components
    parameters: Optional[List[DocParam]] = Field(
        default_factory=list,
        description="List of parameters as defined in the function/method signature. Each includes a symbol name, type (symbol), and explanation."
    )
    returns: Optional[DocReturn] = Field(
        None,
        description="Information about the return value. Type should be a code symbol; description should be in natural language."
    )
    raises: Optional[List[DocRaise]] = Field(
        default_factory=list,
        description="Exceptions (symbols) that may be raised during execution. Include the symbol and a natural language description."
    )
    examples: Optional[List[DocExample]] = Field(
        default_factory=list,
        description="Code examples showing how this symbol is used. Must be syntactically valid. Description should explain what the example does."
    )

    # Optional tags and annotations
    version: Optional[str] = Field(
        None,
        description="Version number as a string (e.g., '1.0.0'). Used for documentation purposes only."
    )
    author: Optional[str] = Field(
        None,
        description="Name of the author or maintainer of the code entity. Plain text."
    )
    deprecated: bool = Field(
        False,
        description="Boolean flag to indicate if this symbol is deprecated. If True, docstring should include a deprecation notice."
    )
    todo: Optional[List[str]] = Field(
        default_factory=list,
        description="List of pending TODO items in natural language related to this symbol."
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="List of keywords (symbols or labels) for grouping or indexing the documented entity."
    )
    member_of: Optional[str] = Field(
        None,
        description="Name of the enclosing class or module (symbol) to which this entity belongs, for context."
    )
    template: Optional[str] = Field(
        None,
        description="Generic template symbol used for generics (e.g., 'T', 'K, V'). This should match the language's generic syntax."
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes or context in natural language that do not fit into other fields. This can include implementation details, performance considerations, or usage patterns."
    )
    async_func: Optional[bool] = Field(
        False,
        description="True if the function or method uses asynchronous behavior (e.g., declared with 'async' in Python)."
    )
    visibility: Literal["public", "protected", "private"] = Field(
        "public",
        description="Access modifier (symbol) used in class/object context. Must be one of 'public', 'protected', or 'private'."
    )

class LowComplexityDocstringSchema(DocstringSchema):
    """
    A simplified version of the DocstringSchema for low-complexity functions.
    This schema is used when the function does not require detailed documentation.
    It includes only the essential fields.
    """
    short_description: str = Field(
        None,
        description="One-line summary in natural language of what the function, method, or class does."
    )

class MediumComplexityDocstringSchema(LowComplexityDocstringSchema):
    """
    A more detailed version of the DocstringSchema for medium-complexity functions.
    This schema includes a short description, a long description, and optional parameters.
    It is used when the function requires a brief overview and some explanation of its parameters.
    """
    short_description: str = Field(
        None,
        description="One-line summary in natural language of what the function, method, or class does."
    )
    long_description: str = Field(
        None,
        description="Extended description in natural language. Can include context, usage notes, assumptions, and inline references to symbols using consistent notation."
    )
class HighComplexityDocstringSchema(MediumComplexityDocstringSchema):
    """
    A comprehensive version of the DocstringSchema for high-complexity functions.
    This schema includes all fields, providing detailed documentation for complex functions.
    """
    parameters: List[DocParam] = Field(
        default_factory=list,
        description="List of parameters as defined in the function/method signature. Each includes a symbol name, type (symbol), and explanation."
    )
    returns: DocReturn = Field(
        None,
        description="Information about the return value. Type should be a code symbol; description should be in natural language."
    )
    raises: List[DocRaise] = Field(
        default_factory=list,
        description="Exceptions (symbols) that may be raised during execution. Include the symbol and a natural language description."
    )

class VeryHighComplexityDocstringSchema(HighComplexityDocstringSchema):
    """
    An extended version of the DocstringSchema for very high-complexity functions.
    This schema includes all fields, providing detailed documentation for very complex functions.
    It is used when the function requires extensive documentation, including examples and notes.
    """
    examples: List[DocExample] = Field(
        default_factory=list,
        description="Code examples showing how this symbol is used. Must be syntactically valid. Description should explain what the example does."
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes or context in natural language that do not fit into other fields. This can include implementation details, performance considerations, or usage patterns."
    )