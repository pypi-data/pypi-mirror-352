import enum
import inspect
import logging
from collections.abc import Callable
from typing import Any, get_args, get_origin

from docstring_parser import Docstring, DocstringParam, parse
from pydantic import BaseModel

from pse.types.json.schema_sources.from_pydantic import pydantic_to_schema

logger = logging.getLogger(__name__)


def callable_to_schema(function: Callable) -> dict[str, Any]:
    """
    Generate a schema for the specified Python function.

    This takes a callable and parses its signature and docstring,
    and constructs a schema representing the function's parameters.

    Args:
        function (Callable): The Python function to generate a schema for.

    Returns:
        dict[str, Any]: A dictionary representing the JSON schema of the function's parameters.
    """
    sig = inspect.signature(function)
    docstring = parse(function.__doc__ or "No docstring provided")

    schema: dict[str, Any] = {
        "name": function.__name__,
        "description": docstring.description,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    param_index = 0
    for param in sig.parameters.values():
        if param.name == "self":
            continue  # skip 'self' parameter

        param_docstring = (
            docstring.params[param_index]
            if len(docstring.params) > param_index
            else None
        )
        param_schema = parameter_to_schema(param, param_docstring, docstring)
        schema["parameters"]["properties"][param.name] = param_schema

        if param.default is inspect.Parameter.empty and param_schema.get("nullable", False) is False:
            schema["parameters"]["required"].append(param.name)

        param_index += 1

    # Handle the case when all parameters are nullable with defaults
    if not schema["parameters"]["required"]:
        del schema["parameters"]["required"]
        schema["parameters"]["nullable"] = True

    return schema


def parameter_to_schema(
    param: inspect.Parameter,
    param_docstring: DocstringParam | None,
    docstring: Docstring
) -> dict[str, Any]:
    """
    Generate a schema for a function parameter.

    Args:
        param (inspect.Parameter): The parameter to generate a schema for.
        docstring (Docstring): The docstring for the function.
    """

    parameter_schema: dict[str, Any] = {}
    if param_docstring:
        parameter_schema["description"] = param_docstring.description or docstring.short_description or ""

    if inspect.isclass(param.annotation) and issubclass(param.annotation, BaseModel):
        # Use Pydantic model if the parameter is a BaseModel subclass
        return pydantic_to_schema(param.annotation)
    elif param.annotation == inspect.Parameter.empty:
        logger.warning(f"Parameter '{param.name}' lacks type annotation.")
        parameter_schema["type"] = "any"
        return parameter_schema
    elif param.default is not inspect.Parameter.empty:
        default_value = param.default
        if default_value is None:
            parameter_schema["nullable"] = True
        else:
            parameter_schema["default"] = default_value
    #######
    parameter_type_schemas = []
    parameter_arguments = get_args(param.annotation)

    # Special handling for direct dict type
    origin = get_origin(param.annotation)
    if origin is dict:
        dict_schema = {
            "type": "object",
            "additionalProperties": {"type": "any"}
        }
        args = get_args(param.annotation)
        if len(args) > 1:
            value_type = args[1]
            dict_schema["additionalProperties"] = {
                "type": get_type(value_type)
            }
        # Preserve the description if it exists
        if param_docstring:
            dict_schema["description"] = param_docstring.description or ""
        return dict_schema

    # Process union types and other types.
    parameter_type_schemas: list[dict[str, Any]] = []
    for argument in parameter_arguments or [param.annotation]:
        parameter_type_schema: dict[str, Any] = {}
        arg_origin = get_origin(argument)
        parameter_type = get_type(argument)

        if arg_origin is dict:
            parameter_type_schema["type"] = "object"
            args = get_args(argument)
            #  Consider using get, or a guard clause.
            if len(args) > 1:
                parameter_type_schema["additionalProperties"] = {
                    "type": get_type(args[1])
                }
        elif parameter_type == "null":
            parameter_schema["nullable"] = True
            continue  # Skip adding to type_schemas.
        elif parameter_type in ("array", "set"):
            parameter_type_schema["type"] = parameter_type
            if args := get_args(argument):
                parameter_type_schema["items"] = {"type": get_type(args[0])}
        elif parameter_type == "enum" and issubclass(argument, enum.Enum):
            parameter_type_schema["enum"] = [
                member.value for member in argument
            ]  # More concisely.
        elif parameter_type:
            parameter_type_schema["type"] = parameter_type

        if parameter_type_schema:
            parameter_type_schemas.append(parameter_type_schema)

    # Simplify the logic for setting the final schema type, handling edge cases.
    match len(parameter_type_schemas):
        case 0:
            # If no types were added and it wasn't nullable, default to "any".
            if "nullable" not in parameter_schema:
                parameter_schema["type"] = "any"
        case 1:
            # Merge the single schema into the main schema.
            parameter_schema.update(parameter_type_schemas[0])

    if len(parameter_type_schemas) > 1:
        parameter_schema["type"] = parameter_type_schemas
    elif parameter_type_schemas:
        parameter_schema.update(**parameter_type_schemas[0])
    else:
        parameter_schema["type"] = "any"

    return parameter_schema

def get_type(python_type: Any) -> str:
    """Map a Python type to a JSON schema type."""
    if python_type is type(None):
        return "null"

    type_name = get_origin(python_type) or python_type
    type_map: dict[type | Any, str] = {
        int: "integer",
        str: "string",
        bool: "boolean",
        float: "number",
        list: "array",
        dict: "object",
        tuple: "array",
        set: "set",
        enum.EnumType: "enum",
        type(None): "null",
        BaseModel: "object",
        Any: "any",
    }
    if type_name not in type_map:
        if type(python_type) in type_map:
            return type_map[type(python_type)]

        logger.warning(f"Unknown type: {python_type}")
        return "any"

    return type_map[type_name]
