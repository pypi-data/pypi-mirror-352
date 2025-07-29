"""Compatibility checks for MCP servers."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class MCPServerProtocol(Protocol):
    """Protocol for MCP server compatibility."""

    def list_tools(self) -> Any:
        """List available tools."""
        ...

    def call_tool(self, name: str, arguments: dict) -> Any:
        """Call a tool by name."""
        ...


def is_fastmcp_server(server: Any) -> bool:
    """Check if the server is a FastMCP instance."""
    # Check for FastMCP class name or specific attributes
    return hasattr(server, "_mcp_server")

def has_neccessary_attributes(server: Any) -> bool:
    """Check if the server has necessary attributes for compatibility."""
    required_methods = ["list_tools", "call_tool"]
    
    # Check for core methods that both FastMCP and Server implementations have
    for method in required_methods:
        if not hasattr(server, method):
            return False
    
    # For FastMCP servers, verify internal MCP server exists
    if hasattr(server, "_mcp_server"):
        # FastMCP server - check that internal MCP server has request_context
        # Use dir() to avoid triggering property getters that might raise exceptions
        if "request_context" not in dir(server._mcp_server):
            return False
        # Check for get_context method which is FastMCP specific
        if not hasattr(server, "get_context"):
            return False
        # Check for request_handlers dictionary on internal server
        if not hasattr(server._mcp_server, "request_handlers"):
            return False
        if not isinstance(server._mcp_server.request_handlers, dict):
            return False
    else:
        # Regular Server implementation - check for request_context directly
        # Use dir() to avoid triggering property getters that might raise exceptions
        if "request_context" not in dir(server):
            return False
        # Check for request_handlers dictionary
        if not hasattr(server, "request_handlers"):
            return False
        if not isinstance(server.request_handlers, dict):
            return False
    
    return True


def is_compatible_server(server: Any) -> bool:
    """Check if the server is compatible with MCPCat."""
    return has_neccessary_attributes(server)
