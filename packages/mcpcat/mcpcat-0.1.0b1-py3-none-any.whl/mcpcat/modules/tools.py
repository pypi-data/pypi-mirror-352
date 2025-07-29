"""Tool management and interception for MCPCat."""

from typing import Any, TYPE_CHECKING

from mcp import ServerResult, Tool
from mcp.types import CallToolRequest, CallToolResult, ListToolsRequest, TextContent

from mcpcat.modules.tracing import record_trace
from mcpcat.modules.version_detection import has_fastmcp_support

from ..types import MCPCatData
from .logging import log_info
from .session import capture_session_info

if TYPE_CHECKING or has_fastmcp_support():
    try:
        from mcp.server import FastMCP
    except ImportError:
        FastMCP = None

async def handle_report_missing(arguments: dict[str, Any], data: MCPCatData) -> CallToolResult:
    """Handle the report_missing tool."""
    missing_tool = arguments.get("missing_tool", "")
    description = arguments.get("description", "")

    # Log the report
    log_info("Missing tool reported", {
        "missing_tool": missing_tool,
        "description": description,
    }, data.options)

    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=f"Thank you for reporting that you need a '{missing_tool}' tool. This feedback helps improve the server."
            )
        ]
    )
