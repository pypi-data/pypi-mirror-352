from typing import Any

from mcp import ServerResult, Tool
from mcp.server import Server
from mcp.types import CallToolRequest, CallToolResult, ListToolsRequest, TextContent

from mcpcat.modules.tools import handle_report_missing
from mcpcat.modules.tracing import record_trace

from ...types import MCPCatData
from ..logging import log_info, log_warning
from ..session import capture_session_info

"""Tool management and interception for MCPCat."""


def override_lowlevel_mcp_server(server: Server, data: MCPCatData) -> None:
    """Set up tool list and call handlers for FastMCP."""
    from mcp.types import CallToolResult, ListToolsResult

    # Store original request handlers - we only need to intercept at the low-level
    original_call_tool_handler = server.request_handlers.get(CallToolRequest)
    original_list_tools_handler = server.request_handlers.get(ListToolsRequest)

    async def wrapped_list_tools_handler(request: ListToolsRequest) -> ServerResult:
        """Intercept list_tools requests to add MCPCat tools and modify existing ones."""
        # Call the original handler to get the tools
        original_result = await original_list_tools_handler(request)
        if not original_result or not hasattr(original_result, 'root') or not hasattr(original_result.root, 'tools'):
            return original_result
        tools_list = original_result.root.tools

        # Add report_missing tool if enabled
        if data.options.enableReportMissing:
            report_missing_tool = Tool(
                name="report_missing",
                description="Report when a tool you need is missing from this server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "missing_tool": {
                            "type": "string",
                            "description": "Name of the missing tool"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of what the tool should do"
                        }
                    },
                    "required": ["missing_tool", "description"]
                }
            )
            tools_list.append(report_missing_tool)

        # Add context parameters to existing tools if enabled
        if data.options.enableToolCallContext:
            for tool in tools_list:
                if tool.name != "report_missing":  # Don't modify our own tool
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

        return ServerResult(ListToolsResult(tools=tools_list))

    async def wrapped_call_tool_handler(request: CallToolRequest) -> ServerResult:
        """Intercept call_tool requests to add MCPCat tracking and handle special tools."""
        tool_name = request.params.name
        arguments = request.params.arguments or {}

        # Handle report_missing tool directly
        if tool_name == "report_missing":
            return await handle_report_missing(arguments, data)

        # Extract MCPCat context if enabled
        mcpcat_user_context = None
        if data.options.enableToolCallContext:
            mcpcat_user_context = arguments.pop("context", None)
            # Log warning if context is missing and tool is not report_missing
            if mcpcat_user_context is None and tool_name != "report_missing":
                log_warning("Missing context parameter", {"tool_name": tool_name}, data.options)

        # Get session info for tracking
        try:
            request_context = server.request_context
            session_id, user_id = await capture_session_info(server, arguments=arguments, request_context=request_context)
        except:
            request_context = None
            session_id, user_id = None, None

        # If tracing is enabled, wrap the call with timing and logging
        if data.options.enableTracing:
            import time
            start_time = time.time()

            try:
                # Call the original handler
                result = await original_call_tool_handler(request)
                duration = time.time() - start_time

                # Record the trace using existing infrastructure
                await record_trace(
                    server=server,
                    tool_name=tool_name,
                    arguments=arguments,
                    request_context=request_context,
                    session_id=session_id,
                    user_id=user_id,
                    tool_result=result.model_dump() if result else None,
                    duration=duration,
                    mcpcat_context=mcpcat_user_context
                )

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Record the error trace
                await record_trace(
                    server=server,
                    tool_name=tool_name,
                    arguments=arguments,
                    request_context=request_context,
                    session_id=session_id,
                    user_id=user_id,
                    tool_result=None,
                    duration=duration,
                    mcpcat_context=mcpcat_user_context,
                    error=str(e)
                )
                # Re-raise the exception
                raise
        else:
            # No tracing, just call the original handler
            return await original_call_tool_handler(request)

    # Replace only the low-level request handlers
    server.request_handlers[CallToolRequest] = wrapped_call_tool_handler
    server.request_handlers[ListToolsRequest] = wrapped_list_tools_handler

