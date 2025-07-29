"""Test error tracking functionality."""

import os
from pathlib import Path

import pytest

from mcpcat import track
from mcpcat.modules.internal import get_mcpcat_data
from mcpcat.types import MCPCatOptions

from .test_utils import LOG_FILE, cleanup_log_file
from .test_utils.client import create_test_client
from .test_utils.todo_server import create_todo_server


class TestErrorTracking:
    """Test error tracking functionality."""
    def setup_method(self):
        """Clean up log file before each test."""
        cleanup_log_file()

    def teardown_method(self):
        """Clean up log file after each test."""
        cleanup_log_file()

    @pytest.mark.asyncio
    async def test_track_exceptions_as_errors(self):
        """Should track exceptions as errors."""
        server = create_todo_server()

        # Add tool that throws an error
        @server.tool()
        def throw_error(context: str = None) -> str:
            """Tool that throws an exception."""
            raise Exception("Unexpected exception occurred")

        # Track the server
        track(server, MCPCatOptions(enableTracing=True))

        # Test exception case
        async with create_test_client(server) as client:
            result = await client.call_tool("throw_error", {"context": "Testing exception"})
            # Verify the error is returned as an error result
            assert result.isError is True
            assert "Unexpected exception occurred" in result.content[0].text

        # Check logs
        log_content = Path(LOG_FILE).read_text()
        assert "throw_error" in log_content
        assert "Unexpected exception occurred" in log_content

        # Check traces
        tracking_data = get_mcpcat_data(server)
        exception_trace = next((t for t in tracking_data.traces if t.tool_name == "throw_error"), None)

        assert exception_trace is not None


    @pytest.mark.asyncio
    async def test_handle_successful_tool_calls_correctly(self):
        """Should handle successful tool calls correctly."""
        server = create_todo_server()
        track(server, MCPCatOptions(enableTracing=True))

        async with create_test_client(server) as client:
            result = await client.call_tool("list_todos", {"context": "Listing todos"})

            # Should not have isError flag
            assert result.isError is False

        log_content = Path(LOG_FILE).read_text()
        assert "list_todos" in log_content

        # Check trace doesn't have isError flag
        tracking_data = get_mcpcat_data(server)
        success_trace = next((t for t in tracking_data.traces if t.tool_name == "list_todos"), None)
        assert success_trace is not None
        assert success_trace.is_error is False

    @pytest.mark.asyncio
    async def test_track_tool_errors_with_isError_true(self):
        """Should track tool errors when CallToolResult has isError=True."""
        server = create_todo_server()

        # Create a tool that returns CallToolResult with isError=True
        @server.tool()
        def application_error_todo(text: str, context: str = None) -> str:
            """Add todo that returns an application error."""
            raise Exception("Database is locked, cannot add todo")

        # Track the server
        track(server, MCPCatOptions(enableTracing=True))

        # Call the tool that will return an error result
        async with create_test_client(server) as client:
            result = await client.call_tool("application_error_todo", {
                "text": "Test todo",
                "context": "Testing application error"
            })

            # Verify the result has isError=True
            assert result.isError is True
            assert len(result.content) == 1
            assert "Database is locked, cannot add todo" in result.content[0].text

        # Check the log contains the error
        assert os.path.exists(LOG_FILE)
        log_content = Path(LOG_FILE).read_text()
        assert "application_error_todo" in log_content
        assert "Database is locked, cannot add todo" in log_content

        # Check that the trace was recorded with error info
        tracking_data = get_mcpcat_data(server)
        assert tracking_data is not None
        error_trace = next((t for t in tracking_data.traces if t.tool_name == "application_error_todo"), None)
        assert error_trace is not None
        assert error_trace.is_error is True
        assert "Database is locked, cannot add todo" in error_trace.response

    @pytest.mark.asyncio
    async def test_track_tool_errors_with_different_formats(self):
        """Should track tool errors with different result formats."""
        server = create_todo_server()

        # Create a tool that returns error as JSON in text content
        @server.tool()
        def json_error_todo(text: str, context: str = None) -> str:
            raise Exception("Permission denied: insufficient privileges")

        # Create a tool that returns dict result with isError
        @server.tool()
        def dict_error_todo(text: str, context: str = None) -> dict:
            """Add todo that returns error as dict."""
            raise Exception( {
                "error": "Validation failed: text too long",
                "result": None
            })

        # Track the server
        track(server, MCPCatOptions(enableTracing=True))

        # Test JSON error format
        async with create_test_client(server) as client:
            json_result = await client.call_tool("json_error_todo", {
                "text": "Test todo",
                "context": "Testing JSON error"
            })

            # Check result - error is now returned as isError=True
            assert json_result.isError is True
            assert len(json_result.content) == 1
            assert "Permission denied" in json_result.content[0].text

        # Test dict error format
        async with create_test_client(server) as client:
            dict_result = await client.call_tool("dict_error_todo", {
                "text": "Very long text " * 100,
                "context": "Testing dict error"
            })

            # The dict should be converted to CallToolResult by MCP
            assert len(dict_result.content) == 1

        # Check logs for both errors
        log_content = Path(LOG_FILE).read_text()
        assert "json_error_todo" in log_content
        assert "dict_error_todo" in log_content
        assert "Permission denied" in log_content
        assert "Validation failed" in log_content

        # Check traces
        tracking_data = get_mcpcat_data(server)
        json_trace = next((t for t in tracking_data.traces if t.tool_name == "json_error_todo"), None)
        dict_trace = next((t for t in tracking_data.traces if t.tool_name == "dict_error_todo"), None)

        assert json_trace is not None
        assert dict_trace is not None

    @pytest.mark.asyncio
    async def test_error_message_extraction_from_content(self):
        """Should extract error messages from CallToolResult content arrays."""
        server = create_todo_server()

        # Create a tool that returns error with multiple content items
        @server.tool()
        def multi_content_error(text: str, context: str = None) -> dict:
            """Tool that returns error with multiple content items."""
            raise Exception(
                ["Error: Operation failed", "Details: The requested resource is unavailable"]
            )

        # Track the server
        track(server, MCPCatOptions(enableTracing=True))

        # Call the tool
        async with create_test_client(server) as client:
            result = await client.call_tool("multi_content_error", {
                "text": "Test",
                "context": "Testing error extraction"
            })

            assert result.isError is True
            assert "Operation failed" in result.content[0].text
            assert "requested resource is unavailable" in result.content[0].text

        # Check that error messages were properly extracted and logged
        log_content = Path(LOG_FILE).read_text()
        assert "multi_content_error" in log_content
        assert "Operation failed" in log_content
        assert "requested resource is unavailable" in log_content

        # Check trace contains the error message
        tracking_data = get_mcpcat_data(server)
        error_trace = next((t for t in tracking_data.traces if t.tool_name == "multi_content_error"), None)
        assert error_trace is not None
        assert error_trace.is_error is True
        # The error should contain at least the first content item
        assert "Operation failed" in error_trace.response or "resource is unavailable" in error_trace.response
