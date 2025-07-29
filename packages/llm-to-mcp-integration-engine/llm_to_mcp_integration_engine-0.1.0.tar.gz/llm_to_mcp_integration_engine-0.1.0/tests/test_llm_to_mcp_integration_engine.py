import pytest
from src.llm_to_mcp_integration_engine.llm_to_mcp_integration_engine import llm_to_mcp_integration_advance, llm_to_mcp_integration_default, llm_to_mcp_integration_custom
from src.llm_to_mcp_integration_engine.exceptions import InvalidFormatError, RetryLimitExceededError

def test_pure_json_valid_selected_tools_case():
    """Unit tests for pure-JSON valid `SELECTED_TOOLS` case"""
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
    assert result == {"success": True, "results": ['Tool 1 executed with params: {\'param1\': \'value1\'}', 'Tool 2 executed with params: {\'param3\': True}}']}


def test_non_json_case_with_embedded_json_fragment():
    """Unit tests for non-JSON case with embedded JSON fragment"""
    tools_list = {
        "tool1": [{"name": "param1", "type": "str", "required": True}, {"name": "param2", "type": "int", "required": False}],
        "tool2": [{"name": "param3", "type": "bool", "required": True}]
    }
    llm_response = 'Here is some text with a JSON: {"SELECTED_TOOLS": [{"tool_name": "tool1", "parameters": {"param1": "value1"}},{"tool_name": "tool2", "parameters": {"param3": true}}]}'
    result = llm_to_mcp_integration_advance(tools_list, llm_response, False, False, False)
    assert result == {"success": True, "results": ['Tool 1 executed with params: {\'param1\': \'value1\'}', 'Tool 2 executed with params: {\'param3\': True}}']}


def test_single_selected_tool():
    """Unit tests for single `SELECTED_TOOL`"""
    tools_list = {
        "tool1": [{"name": "param1", "type": "str", "required": True}, {"name": "param2", "type": "int", "required": False}],
        "tool2": [{"name": "param3", "type": "bool", "required": True}]
    }
    llm_response = {
        "SELECTED_TOOL": "tool1", "parameters": {"param1": "value1"}
    }
    result = llm_to_mcp_integration_advance(tools_list, llm_response, True, False, False)
    assert result == {"success": True, "results": ['Tool 1 executed with params: {\'param1\': \'value1\'}']}


def test_no_tools_selected():
    """Unit tests for `NO_TOOLS_SELECTED`"""
    tools_list = {
        "tool1": [{"name": "param1", "type": "str", "required": True}, {"name": "param2", "type": "int", "required": False}],
        "tool2": [{"name": "param3", "type": "bool", "required": True}]
    }
    llm_response = {
        "NO_TOOLS_SELECTED": True
    }
    result = llm_to_mcp_integration_advance(tools_list, llm_response, True, False, False)
    assert result == {"success": True, "results": []}


def test_missing_cot_triggers_retry():
    """Unit tests for missing CoT → triggers retry"""
    tools_list = {
        "tool1": [{"name": "param1", "type": "str", "required": True}, {"name": "param2", "type": "int", "required": False}],
        "tool2": [{"name": "param3", "type": "bool", "required": True}]
    }
    llm_response = {
        "SELECTED_TOOL": "tool1", "parameters": {"param1": "value1"}, "chain_of_thought": "short"
    }
    with pytest.raises(Exception):
        llm_to_mcp_integration_advance(tools_list, llm_response, True, False, False)


def test_retry_limit_exceeded():
    """Unit tests for retry limit exceeded"""
    tools_list = {
        "tool1": [{"name": "param1", "type": "str", "required": True}, {"name": "param2", "type": "int", "required": False}],
        "tool2": [{"name": "param3", "type": "bool", "required": True}]
    }
    llm_response = {
        "SELECTED_TOOL": "tool1", "parameters": {"param1": "value1"}
    }
    with pytest.raises(Exception):
        llm_to_mcp_integration_advance(tools_list, llm_response, True, False, False)


def test_actual_chaining_of_two_mock_tools():
    """Unit tests for actual chaining of two mock tools"""
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
    assert result == {"success": True, "results": ['Tool 1 executed with params: {\'param1\': \'value1\'}', 'Tool 2 executed with params: {\'param3\': True}}']}

def test_default_selected_tool_single_call():
    # Given
    tools_list = {"PingTool": [{"name": "param1", "type": "str"}]}
    llm_response = {
        "SELECTED_TOOL": {
            "name": "PingTool",
            "parameters": {"param1": "hello"}
        }
    }

    # When
    result = llm_to_mcp_integration_default(tools_list, llm_response, json_validation=True)

    # Then
    assert result == {"success": True, "results": ["Tool 1 executed with params: {'param1': 'hello'}"]}

def test_default_rejects_no_tools_selected():
    tools_list = {}
    llm_response = {"NO_TOOLS_SELECTED": True}
    with pytest.raises(InvalidFormatError):
        llm_to_mcp_integration_default(tools_list, llm_response, json_validation=True)

def test_default_multiple_directives_error():
    tools_list = {}
    llm_response = {
        "SELECTED_TOOL": {"name": "PingTool", "parameters": {"param1": "hello"}},
        "NO_TOOLS_SELECTED": True
    }
    with pytest.raises(InvalidFormatError):
        llm_to_mcp_integration_default(tools_list, llm_response, json_validation=True)

def test_custom_html_param():
    tools_list = {
        "RenderHTML": [{"name": "html", "type": "str"}]
    }
    llm_response = {
        "SELECTED_TOOL": {
            "name": "RenderHTML",
            "parameters": {"html": "<div>Hello</div>"}
        }
    }

    result = llm_to_mcp_integration_custom(tools_list, llm_response, json_validation=True)

    assert result == {"success": True, "results": ["Tool 1 executed with params: {'html': '<div>Hello</div>'}"]}

def test_custom_supports_no_tools_selected():
    tools_list = {}
    llm_response = {"NO_TOOLS_SELECTED": True}
    result = llm_to_mcp_integration_custom(tools_list, llm_response, json_validation=True)
    assert result == {"success": True, "results": []}
