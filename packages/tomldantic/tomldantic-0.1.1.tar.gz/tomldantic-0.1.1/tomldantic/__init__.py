"""tomldantic - A library to convert Pydantic models to TOML templates."""

from enum import Enum
from pathlib import Path
from typing import Any, Type

from pydantic import BaseModel

NEWLINE = "\n"


class EPropType(Enum):
    """Enum for property types in the schema."""

    ARRAY = "array"


def _to_str(type_, value):
    """Convert a value to a string representation based on its type."""
    # the type_map is used to convert the type to a string representation
    type_map = {"string": f'"{value}"'}

    # if the type is in type_map then we return the mapped value
    if type_ in type_map:
        return type_map[type_]

    return value


def _get_default_value(
    json_schema: dict[str, Any], prop_name: str, prop_item: dict[str, Any]
) -> str:
    """Get the default value of a property item.

    if the type is an array then we need to handle it by checking the
    items type and if it has a reference which means we need to go
    deeper.
    """
    prop_default = prop_item["default"]
    prop_type = prop_item.get("type")
    out_str = ""

    if prop_type == EPropType.ARRAY.value:
        items_type = prop_item["items"].get("type")
        items_ref = prop_item["items"].get("$ref")
        if items_ref:
            items_definition = json_schema["$defs"][items_ref.split("/")[-1]]
            out_str += f"[[{prop_name}]]" + NEWLINE
            out_str += _json_schema_to_toml(items_definition)
        else:
            # if the items type is not a reference then we can just
            # convert the items to a string representation
            out_str += f"{prop_name} = ["
            out_str += ", ".join(_to_str(items_type, item) for item in prop_default)
            out_str += "]"
    else:
        out_str += f"{prop_name} = {_to_str(prop_type, prop_default)}"

    return out_str


def _json_schema_to_toml(json_schema: dict[str, Any]) -> str:
    """Convert a Pydantic JSON schema to a TOML template string.

    :param json_schema: The JSON schema to convert.
    :return: A string representing the TOML template.
    """
    out_str = ""

    # if we have a description in the schema then add it as a comment
    if "description" in json_schema:
        out_str += NEWLINE + "# " + json_schema["description"] + NEWLINE + NEWLINE

    # if we have properties in the schema then we iterate over them
    if "properties" in json_schema:
        # get all properties
        properties = json_schema["properties"]
        for prop_name, prop_item in properties.items():
            prop_default = prop_item.get("default")
            prop_type = prop_item.get("type")
            prop_ref = prop_item.get("$ref")
            prop_description = prop_item.get("description")

            # is there a reference then we go deeper
            if prop_ref:
                prop_definition = json_schema["$defs"][prop_ref.split("/")[-1]]
                out_str += f"[{prop_name}]" + NEWLINE

                # recursively add definition of inner objects
                out_str += _json_schema_to_toml(prop_definition)
            else:
                # is there a default for the field then add it otherwise use a placeholder
                if prop_default:
                    out_str += _get_default_value(json_schema, prop_name, prop_item)
                else:
                    out_str += f"{prop_name} = <{prop_type}>"

                # add a description as a comment at the end of the line
                if prop_description:
                    out_str += f"  # {prop_description}"

                # newline
                out_str += NEWLINE

    return out_str


def dumps(model_cls: Type[BaseModel]) -> str:
    """Create a TOML template from a Pydantic model class.

    :param model_cls: The Pydantic model class to dump.
    :return: A string representing the TOML template.
    """
    json_schema = model_cls.model_json_schema()
    return _json_schema_to_toml(json_schema)


def dump(model_class: Type[BaseModel], fn: Path | str) -> None:
    """Dump a Pydantic model class to a TOML file.

    :param model_class: The Pydantic model class to dump.
    :param fn: The file path where the TOML template should be saved.
    """
    out_str = dumps(model_class)
    with open(fn, "w", encoding="utf-8") as f:
        f.write(out_str)
