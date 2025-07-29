from typing import List, Optional, Union

from pydantic import BaseModel


class ToolParam(BaseModel):
    name: str
    type: str
    required: bool


class StepDef(BaseModel):
    step_name: str
    tool_name: str
    parameters: dict


class IntegrationRequest(BaseModel):
    tools_list: dict
    llm_response: Union[str, dict]
    json_validation: bool
    no_tools_selected: bool
    multi_stage_tools_select: bool


class IntegrationResult(BaseModel):
    success: bool
    selected_steps: Optional[List[StepDef]]
    diagnostics: Optional[List[str]]
    retry_needed: bool
    error_details: Optional[str]
