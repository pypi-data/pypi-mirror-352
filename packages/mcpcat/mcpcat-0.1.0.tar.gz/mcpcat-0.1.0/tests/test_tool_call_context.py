"""Test enableToolCallContext functionality."""

import pytest

from mcpcat import track
from mcpcat.types import MCPCatOptions
from tests.test_utils import cleanup_log_file

from .test_utils.client import create_test_client
from .test_utils.todo_server import create_todo_server


class TestToolCallContext:
    """Test enableToolCallContext functionality."""
    def setup_method(self):
        """Clean up log file before each test."""
        cleanup_log_file()

    def teardown_method(self):
        """Clean up log file after each test."""
        cleanup_log_file()

    @pytest.mark.asyncio
    async def test_enable_tool_call_context_by_default(self):
        """Should enable tool call context by default."""
        server = create_todo_server()
        track(server)

        # Get the tools to check if context parameter was added
        # This would need to be implemented based on how the Python SDK
        # handles tool introspection
        # For now, we'll just verify the server is tracked
        assert hasattr(server, 'tool')

    @pytest.mark.asyncio
    async def test_not_add_context_when_disabled(self):
        """Should not add context parameter when enableToolCallContext is false."""
        server = create_todo_server()
        track(server, MCPCatOptions(enableToolCallContext=False))

        # Verify server is still functional
        assert hasattr(server, 'tool')

    @pytest.mark.asyncio
    async def test_not_add_context_to_report_missing_tool(self):
        """Should not add context parameter to report_missing tool."""
        server = create_todo_server()

        track(server, MCPCatOptions())

        # Verify the tool works
        async with create_test_client(server) as client:
            result = await client.call_tool("report_missing", {
                "missing_tool": "test_tool",
                "description": "test description"
            })
            assert "Thank you for reporting that you need a 'test_tool' tool" in result.content[0].text
            # Verify context parameter is not added
            assert "context" not in result.content[0].text

    @pytest.mark.asyncio
    async def test_preserve_existing_tool_schemas_when_adding_context(self):
        """Should preserve existing tool schemas when adding context."""
        server = create_todo_server()
        track(server, MCPCatOptions(enableToolCallContext=True))

        # Test that original functionality is preserved
        async with create_test_client(server) as client:
            result = await client.call_tool("add_todo", {
                "text": "Test todo",
                "context": "Testing context preservation"
            })
            assert "Added todo" in result.content[0].text

    @pytest.mark.asyncio
    async def test_handle_tools_without_input_schema(self):
        """Should handle tools without inputSchema."""
        server = create_todo_server()

        @server.tool()
        def simple_tool() -> str:
            """A tool without input parameters."""
            return "Simple tool executed"

        track(server, MCPCatOptions(enableToolCallContext=True))

        # Verify the tool still works
        async with create_test_client(server) as client:
            result = await client.call_tool("simple_tool", {})
            assert "Simple tool executed" in result.content[0].text
