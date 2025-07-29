"""Test tool call context logging functionality."""

import os
from pathlib import Path

import pytest

from mcpcat import track
from mcpcat.types import MCPCatOptions

from .test_utils import LOG_FILE, cleanup_log_file
from .test_utils.client import create_test_client
from .test_utils.todo_server import create_todo_server


class TestToolCallContextLogging:
    """Test tool call context logging functionality."""

    def setup_method(self):
        """Clean up log file before each test."""
        cleanup_log_file()

    def teardown_method(self):
        """Clean up log file after each test."""
        cleanup_log_file()

    @pytest.mark.asyncio
    async def test_log_warning_when_context_missing(self):
        """Should log warning when context is missing from tool call."""
        server = create_todo_server()
        track(server, MCPCatOptions(enableToolCallContext=True, enableTracing=True))

        # Simulate a tool call without context
        async with create_test_client(server) as client:
            await client.call_tool("add_todo", {"text": "Test todo"})  # No context

        assert os.path.exists(LOG_FILE)
        log_content = Path(LOG_FILE).read_text()
        assert "warning" in log_content
        assert "context" in log_content
        assert "add_todo" in log_content

    @pytest.mark.asyncio
    async def test_log_context_when_present(self):
        """Should log context when present in tool call."""
        server = create_todo_server()
        track(server, MCPCatOptions(enableToolCallContext=True, enableTracing=True))

        # Simulate a tool call with context
        async with create_test_client(server) as client:
            await client.call_tool("add_todo", {
                "text": "Test todo",
                "context": "Adding a test item to verify functionality"
            })

        assert os.path.exists(LOG_FILE)
        log_content = Path(LOG_FILE).read_text()
        assert "Adding a test item to verify functionality" in log_content
        assert "add_todo" in log_content

    @pytest.mark.asyncio
    async def test_not_check_context_for_report_missing_tool(self):
        """Should not check context for report_missing tool."""
        server = create_todo_server()

        # Add report_missing tool
        @server.tool()
        def report_missing(description: str) -> str:
            """Report missing tool functionality."""
            return f"Missing tool reported: {description}"

        track(server, MCPCatOptions(enableToolCallContext=True, enableTracing=True))

        # Simulate a report_missing call without context
        async with create_test_client(server) as client:
            await client.call_tool("report_missing", {
                "description": "Missing feature"
            })  # No context

        assert os.path.exists(LOG_FILE)
        log_content = Path(LOG_FILE).read_text()
        assert "report_missing" in log_content

    @pytest.mark.asyncio
    async def test_not_check_context_when_disabled(self):
        """Should not check context when enableToolCallContext is false."""
        server = create_todo_server()
        track(server, MCPCatOptions(enableToolCallContext=False, enableTracing=True))

        # Simulate a tool call without context
        async with create_test_client(server) as client:
            await client.call_tool("add_todo", {"text": "Test todo"})  # No context

        assert os.path.exists(LOG_FILE)
        log_content = Path(LOG_FILE).read_text()
        assert "add_todo" in log_content

    @pytest.mark.asyncio
    async def test_log_normally_when_tracing_disabled(self):
        """Should log normally when tracing is disabled."""
        server = create_todo_server()
        track(server, MCPCatOptions(enableToolCallContext=False, enableTracing=False))

        # Simulate a tool call without context
        async with create_test_client(server) as client:
            await client.call_tool("add_todo", {"text": "Test todo"})  # No context

        # Should not create tool_call log entries since tracing is disabled
        if os.path.exists(LOG_FILE):
            log_content = Path(LOG_FILE).read_text()
            # Check that no tool_call events were logged (only info events for init)
            assert "add_todo" not in log_content
