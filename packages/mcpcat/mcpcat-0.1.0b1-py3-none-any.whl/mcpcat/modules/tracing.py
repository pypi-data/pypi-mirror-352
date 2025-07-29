"""Tool call tracing for MCPCat."""

import json
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from mcp import Tool

from ..types import Trace
from .logging import log_trace


async def record_trace(
    server: Any,
    tool_name: str,
    arguments: dict[str, Any],
    request_context: Any,
    session_id: str | None,
    user_id: str | None,
    tool_result: Any,
    duration: float,
    mcpcat_context: str | None = None,
    error: str | None = None
) -> None:
    """Record trace information for a tool call."""
    from .internal import get_mcpcat_data
    # Check if call result is an error using the isError property or passed error
    is_error = False
    response = ""
    # handle unexpected exception raised
    if error:
        response = error
        is_error = True
    # handle application error in tool result
    elif 'isError' in tool_result:
        is_error = tool_result['isError']

    # handle tool content
    if tool_result and 'content' in tool_result:
        # if tool_result is a dict, use its content
        if isinstance(tool_result['content'], dict) or isinstance(tool_result['content'], Sequence):
            response = json.dumps(tool_result['content'], separators=(',', ':'))
        else:
            response = str(tool_result['content'])


    # Get MCPCat data and options
    data = get_mcpcat_data(server)

    # Store the trace
    if data:
        # Debug: verify all values are strings
        context_value = mcpcat_context or ""
        arguments_value = json.dumps(arguments, separators=(',', ':'))
        response_value = response or ""

        trace = Trace(
            timestamp=datetime.now(),
            session_id=session_id or "unknown",
            user_id=user_id or "unknown",
            event_type="tool_call",
            tool_name=tool_name,
            is_error=is_error,
            duration=duration,
            context=context_value,
            arguments=arguments_value,
            response=response_value
        )
        if data.options.enableTracing:
            data.traces.append(trace)
            await log_trace(trace, data.options)

def add_user_context_to_existing_tools(toolList: list[Tool]) -> list[Tool]:
    """Add MCPCat's user intention context to every existing tool."""
    for tool in toolList:
        if not tool.inputSchema:
            tool.inputSchema = {
                "type": "object",
                "properties": {},
                "required": []
            }

        # Add context property if it doesn't exist
        if "context" not in tool.inputSchema.get("properties", {}):
            if "properties" not in tool.inputSchema:
                tool.inputSchema["properties"] = {}

            tool.inputSchema["properties"]["context"] = {
                "type": "string",
                "description": "Describe why you are calling this tool and how it fits into your overall task"
            }

            # Add context to required array if it exists
            if isinstance(tool.inputSchema.get("required"), list):
                if "context" not in tool.inputSchema["required"]:
                    tool.inputSchema["required"].append("context")
            else:
                tool.inputSchema["required"] = ["context"]

    return toolList
