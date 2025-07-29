"""MCPCat - Analytics Tool for MCP Servers."""

from typing import Any, Optional

from mcpcat.modules.overrides.fastmcp import override_fastmcp
from mcpcat.modules.overrides.mcp_server import override_lowlevel_mcp_server

from .modules.compatibility import is_compatible_server, is_fastmcp_server
from .modules.internal import get_mcpcat_data, has_mcpcat_data, set_mcpcat_data
from .modules.logging import log_error, log_info
from .modules.session import get_unknown_or_stdio_session
from .modules.tools import handle_report_missing as handleReportMissing
from .types import MCPCatData, MCPCatOptions, UserData

__version__ = "1.0.0"


def track(server: Any, options: MCPCatOptions | None = None) -> Any:
    """
    Enable analytics tracking for an MCP server.
    
    This function modifies the server's tool handlers to add analytics tracking,
    context parameter injection, and additional MCP tools.
    
    Args:
        server: The MCP server instance (e.g., FastMCP)
        options: Optional configuration options
        
    Raises:
        TypeError: If the server is not compatible
    """
    # Use default options if not provided
    if options is None:
        options = MCPCatOptions()

    # Validate server compatibility
    if not is_compatible_server(server):
        raise TypeError(
            "Server must be a FastMCP instance or MCP Low-level Server instance"
        )

    # Check if already tracked
    if has_mcpcat_data(server):
        log_info(
            "MCPCat already initialized for this server",
            {"server": server.__class__.__name__},
            options
        )
        return server

    # Create and store tracking data
    data = MCPCatData(options=options)
    set_mcpcat_data(server, data)

    try:
        # Set up tool handlers
        if is_fastmcp_server(server):
            override_fastmcp(server, data)
        else:
            override_lowlevel_mcp_server(server, data)

        # Log initialization
        log_info(
            "MCPCat tracking initialized",
            {
                "server": server.__class__.__name__,
                "features": {
                    "context": options.enableToolCallContext,
                    "tracing": options.enableTracing,
                    "report_missing": options.enableReportMissing,
                }
            },
            options
        )
    except Exception as e:
        # Clean up on failure
        if has_mcpcat_data(server):
            # Remove from tracking
            get_mcpcat_data(server)  # This will remove the weak reference

        log_error(
            "Failed to initialize MCPCat",
            e,
            {"server": server.__class__.__name__},
            options
        )

        raise

    # Return the server (like TypeScript version)
    return server


def _getServerTrackingData(server: Any) -> MCPCatData | None:
    """Get server tracking data (for testing)."""
    return get_mcpcat_data(server)

__all__ = [
    "track",
    "get_unknown_or_stdio_session",
    "_getServerTrackingData",
    "handleReportMissing",
    "MCPCatOptions",
    "UserData",
    "__version__",
]
