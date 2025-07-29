from .exceptions import InvalidFormatError
from .registry import mock_registry
from .schema import ToolParam

def validate_tools_list(tools_list: dict):
    """Ensure each tool name exists, params typed"""
    for tool_name, params in tools_list.items():
        tool = mock_registry.get_tool(tool_name)
        if not tool:
            raise InvalidFormatError(f"Tool '{tool_name}' not found in registry")
        for param in params:
            if not isinstance(param, dict):
                raise InvalidFormatError(f"Invalid parameter format for tool '{tool_name}'")
            try:
                ToolParam(**param)
            except Exception as e:
                raise InvalidFormatError(f"Invalid parameter definition for tool '{tool_name}': {e}")


def validate_json_structure(response: dict):
    """Ensure presence of exactly one of `SELECTED_TOOLS` / `SELECTED_TOOL` / `NO_TOOLS_SELECTED`"""
    keys = ["SELECTED_TOOLS", "SELECTED_TOOL", "NO_TOOLS_SELECTED"]
    found_keys = [key for key in keys if key in response]
    if len(found_keys) != 1:
        raise InvalidFormatError(f"Response must contain exactly one of {keys}")


def validate_parameters(tool_name: str, params: dict):
    """Per-tool parameter shapes"""
    tool = mock_registry.get_tool(tool_name)
    if not tool:
        raise InvalidFormatError(f"Tool '{tool_name}' not found in registry")

    for param_def in tool:
        param_name = param_def["name"]
        if param_def["required"] and param_name not in params:
            raise InvalidFormatError(f"Missing required parameter '{param_name}' for tool '{tool_name}'")

        if param_name in params:
            param_value = params[param_name]
            param_type = param_def["type"]
            if param_type == "str" and not isinstance(param_value, str):
                raise InvalidFormatError(f"Parameter '{param_name}' for tool '{tool_name}' must be a string")
            elif param_type == "int" and not isinstance(param_value, int):
                raise InvalidFormatError(f"Parameter '{param_name}' for tool '{tool_name}' must be an integer")
            elif param_type == "bool" and not isinstance(param_value, bool):
                raise InvalidFormatError(f"Parameter '{param_name}' for tool '{tool_name}' must be a boolean")
