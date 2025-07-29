"""Test client utilities for MCPCat tests."""

from contextlib import asynccontextmanager
from typing import Any

from mcp.shared.memory import create_connected_server_and_client_session

try:
    from mcp.server import FastMCP
    HAS_FASTMCP = True
except ImportError:
    FastMCP = None
    HAS_FASTMCP = False


@asynccontextmanager
async def create_test_client(server: Any):
    """Create a test client for the given server.
    
    This creates a properly connected MCP client/server pair with full
    request context support, similar to how a real MCP connection works.
    
    Usage:
        server = create_todo_server()
        track(server, options)
        
        async with create_test_client(server) as client:
            result = await client.call_tool("add_todo", {"text": "Test"})
    """
    # Handle both FastMCP and low-level Server
    if hasattr(server, '_mcp_server'):
        # FastMCP server
        async with create_connected_server_and_client_session(server._mcp_server) as client:
            yield client
    else:
        # Low-level Server
        async with create_connected_server_and_client_session(server) as client:
            yield client


async def call_tool_via_client(server: Any, tool_name: str, arguments: dict[str, Any]) -> Any:
    """Helper to call a tool through a proper client session."""
    async with create_test_client(server) as client:
        result = await client.call_tool(tool_name, arguments)
        return result
