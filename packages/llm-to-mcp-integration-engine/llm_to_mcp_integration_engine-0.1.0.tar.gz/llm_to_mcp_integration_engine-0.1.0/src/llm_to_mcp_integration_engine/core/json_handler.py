from typing import List

from ..schema import StepDef


def parse_selected_tools(response: dict) -> List[StepDef]:
    """Parse the selected tools from the JSON response."""
    tools = response.get("SELECTED_TOOLS")
    if not tools:
        return []
    step_defs = []
    for tool in tools:
        step_name = tool.get("step_name", "")
        tool_name = tool.get("tool_name")
        parameters = tool.get("parameters", {})
        if not tool_name:
            continue
        step_defs.append(StepDef(step_name=step_name, tool_name=tool_name, parameters=parameters))
    return step_defs


def parse_selected_tool(response: dict) -> StepDef:
    """Parse the selected tool from the JSON response."""
    tool_name = response.get("SELECTED_TOOL")
    parameters = response.get("parameters", {})
    if not tool_name:
        return StepDef(step_name="", tool_name="", parameters={})
    return StepDef(step_name="", tool_name=tool_name, parameters=parameters)


def parse_no_tools(response: dict) -> None:
    """Parse the no tools selected from the JSON response."""
    if response.get("NO_TOOLS_SELECTED") == True:
        return None
    return None
