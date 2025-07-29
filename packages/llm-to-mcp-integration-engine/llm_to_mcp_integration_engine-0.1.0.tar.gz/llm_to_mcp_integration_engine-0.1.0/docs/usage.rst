=====
Usage
=====

To use llm_to_mcp_integration_engine in a project::

    import llm_to_mcp_integration_engine

The package exposes three main functions:

*   `llm_to_mcp_integration_advance`: The full-featured engine with all validations and retries enabled.
*   `llm_to_mcp_integration_default`: A simplified version with some features disabled for faster execution.
*   `llm_to_mcp_integration_custom`: A customizable version for agentic behaviors and custom logic.

**Example Usage:**

.. code-block:: python

    from llm_to_mcp_integration_engine import llm_to_mcp_integration_advance

    tools_list = {
        "tool1": [{"name": "param1", "type": "str", "required": True}, {"name": "param2", "type": "int", "required": False}],
        "tool2": [{"name": "param3", "type": "bool", "required": True}]
    }
    llm_response = {
        "SELECTED_TOOLS": [
            {"tool_name": "tool1", "parameters": {"param1": "value1"}},
            {"tool_name": "tool2", "parameters": {"param3": True}}
        ]
    }
    result = llm_to_mcp_integration_advance(tools_list, llm_response, True, False, False)
    print(result)
