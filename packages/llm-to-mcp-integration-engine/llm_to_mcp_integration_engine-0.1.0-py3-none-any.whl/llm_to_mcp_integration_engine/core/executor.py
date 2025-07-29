from typing import Any
from ..registry import mock_registry

def execute_tool(name: str, params: dict) -> Any:
    """Execute each tool by name using the plugin registry."""
    tool = mock_registry.get_tool(name)
    if not tool:
        raise ValueError(f"Tool {name} not found")

    # Assuming tools are simple functions for now
    # In a real system, this would handle HTTP calls, etc.
    if name == "tool1":
        return f"Tool 1 executed with params: {params}"
    elif name == "tool2":
        return f"Tool 2 executed with params: {params}"
    else:
        return None


# handle chaining: pass `result_of_step_X` into subsequent steps
