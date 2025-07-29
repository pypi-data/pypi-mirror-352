"""Handles the execution of individual tool steps."""

import asyncio
from typing import Any, Dict, List, Optional
from .schema import StepDef, ToolParam
from .exceptions import ToolNotFoundError, ExecutionError, ParameterValidationError
from .registry import get_tool_adapter, ToolAdapter # Import base class if needed for type hints
from .logging import logger
from .config import DEFAULT_TOOL_TIMEOUT_SECONDS

async def execute_step(
    step: StepDef,
    tools_list: Dict[str, List[ToolParam]], # Needed for validation/context if adapter doesn't handle it
    timeout: int = DEFAULT_TOOL_TIMEOUT_SECONDS,
    # context: Optional[Dict[str, Any]] = None # Optional context from previous steps
) -> Any:
    """
    Executes a single tool step asynchronously.

    1. Looks up the tool adapter via the registry.
    2. Validates parameters (redundant if already done, but good safety check).
    3. Calls the adapter's run method with parameters.
    4. Handles execution errors and timeouts.

    Args:
        step: The StepDef object defining the tool call.
        tools_list: The definition of available tools (for context/validation).
        timeout: Maximum execution time in seconds.
        # context: Data passed from previous steps (for chaining).

    Returns:
        The result returned by the tool adapter.

    Raises:
        ToolNotFoundError: If the tool adapter cannot be found.
        ParameterValidationError: If parameters are invalid for the tool.
        ExecutionError: If the tool fails during execution or times out.
    """
    tool_name = step.tool_name
    params = step.parameters
    step_id = step.step_id
    logger.info(f"Executing step '{step_id}': tool '{tool_name}' with params: {params}")

    try:
        # 1. Get adapter from registry
        adapter = get_tool_adapter(tool_name)
        if adapter is None:
            logger.error(f"No adapter found for tool '{tool_name}' in registry.")
            raise ToolNotFoundError(f"Tool adapter for '{tool_name}' not found.")

        # 2. Parameter Validation (optional, depends on adapter interface)
        # Adapters might handle their own validation based on ToolParam schema.
        # If not, perform validation here using tools_list.
        # from .validators import validate_tool_selection_and_parameters # Avoid circular import if possible
        # validate_tool_selection_and_parameters(step, tools_list) # Assuming validator exists

        # 3. Execute the tool via adapter
        logger.debug(f"Calling adapter run for tool '{tool_name}'...")
        # Add timeout logic
        try:
            result = await asyncio.wait_for(
                adapter.run(**params), # Assuming adapter has async run method
                timeout=timeout
            )
            logger.info(f"Step '{step_id}' (tool '{tool_name}') executed successfully.")
            logger.debug(f"Result for step '{step_id}': {result}")
            return result
        except asyncio.TimeoutError:
            logger.error(f"Tool '{tool_name}' (step '{step_id}') timed out after {timeout} seconds.")
            raise ExecutionError(f"Tool '{tool_name}' timed out after {timeout} seconds.")
        except Exception as e:
            logger.error(f"Error during execution of tool '{tool_name}' (step '{step_id}'): {e}", exc_info=True)
            # Wrap the original exception
            raise ExecutionError(f"Execution failed for tool '{tool_name}': {e}") from e

    except (ToolNotFoundError, ParameterValidationError) as e:
        # Re-raise validation/lookup errors
        raise e
    except Exception as e:
        # Catch any other unexpected errors during lookup/setup
        logger.error(f"Unexpected error during setup for tool '{tool_name}' (step '{step_id}'): {e}", exc_info=True)
        raise ExecutionError(f"Unexpected error preparing tool '{tool_name}': {e}") from e


async def execute_steps_sequentially(
    steps: List[StepDef],
    tools_list: Dict[str, List[ToolParam]],
    timeout_per_step: int = DEFAULT_TOOL_TIMEOUT_SECONDS
) -> List[Any]:
    """
    Executes a list of steps sequentially, passing context if needed.
    Stops execution if any step fails.

    Args:
        steps: The list of StepDef objects to execute.
        tools_list: The definition of available tools.
        timeout_per_step: Timeout for each individual step.

    Returns:
        A list of results from each successful step execution.

    Raises:
        Propagates exceptions from execute_step (ToolNotFoundError, ExecutionError, etc.)
    """
    results = []
    execution_context = {} # Placeholder for passing results between steps if needed

    logger.info(f"Executing {len(steps)} steps sequentially...")
    for i, step in enumerate(steps):
        logger.info(f"--- Starting Step {i+1}/{len(steps)} ('{step.step_id}') ---")
        try:
            # Pass context if implementing chaining logic later
            # result = await execute_step(step, tools_list, timeout_per_step, context=execution_context)
            result = await execute_step(step, tools_list, timeout_per_step)
            results.append(result)
            # Update context for potential chaining
            # execution_context[step.step_id] = result
            # execution_context[f"result_of_step_{i+1}"] = result # Example key
            logger.info(f"--- Completed Step {i+1}/{len(steps)} ('{step.step_id}') ---")
        except Exception as e:
            logger.error(f"Execution failed at step {i+1} ('{step.step_id}'): {e}. Stopping sequence.")
            # Re-raise the exception to be caught by the integrator/retry handler
            raise e

    logger.info("All steps executed successfully.")
    return results

# Note: Assumes existence of `registry.get_tool_adapter` and adapters having an `async def run(**params)` method.
# Basic sequential execution implemented. Chaining context passing is sketched but not fully implemented.
