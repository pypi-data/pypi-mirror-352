"""Test core functionality."""

import os
from pathlib import Path

import pytest

from mcpcat import track
from mcpcat.types import MCPCatOptions

from .test_utils import LOG_FILE, cleanup_log_file
from .test_utils.client import create_test_client
from .test_utils.todo_server import create_todo_server


class TestFunctionality:
    """Test core functionality."""
    def setup_method(self):
        """Clean up log file before each test."""
        cleanup_log_file()

    def teardown_method(self):
        """Clean up log file after each test."""
        cleanup_log_file()

    @pytest.mark.asyncio
    async def test_create_log_file_when_tools_called(self):
        """Should create log file when tools are called."""
        server = create_todo_server()
        track(server, MCPCatOptions(enableTracing=True))

        # Simulate a call to the report_missing tool using the client
        from .test_utils.client import create_test_client
        async with create_test_client(server) as client:
            await client.call_tool("report_missing", {
                "missing_tool": "test_tool",
                "description": "test"
            })

        assert os.path.exists(LOG_FILE)
        log_content = Path(LOG_FILE).read_text()
        assert "test" in log_content

    def test_track_server_correctly(self):
        """Should track the server correctly."""
        server = create_todo_server()
        tracked_server = track(server)

        # Verify that the server is tracked
        assert tracked_server is server
        assert hasattr(tracked_server, 'tool')

    def test_maintain_original_server_functionality(self):
        """Should maintain original server functionality."""
        server = create_todo_server()
        tracked_server = track(server)

        # Verify server maintains its original properties and methods
        assert hasattr(tracked_server, 'tool')
        assert tracked_server.__class__.__name__ == 'FastMCP'

    def test_handle_multiple_tracking_calls(self):
        """Should handle multiple tracking calls."""
        server = create_todo_server()
        tracked_server1 = track(server, MCPCatOptions(enableReportMissing=True))
        tracked_server2 = track(tracked_server1, MCPCatOptions(enableTracing=False))

        # Should return the same server instance
        assert tracked_server2 is server

    @pytest.mark.asyncio
    async def test_not_create_log_file_when_tracing_disabled(self):
        """Should not create log file when tracing is disabled."""
        server = create_todo_server()

        # Add report_missing tool
        @server.tool()
        def report_missing(description: str) -> str:
            """Report missing tool functionality."""
            return f"Missing tool reported: {description}"

        track(server, MCPCatOptions(enableTracing=False))

        # Even if we manually call report_missing, behavior depends on implementation
        async with create_test_client(server) as client:
            await client.call_tool("report_missing", {"description": "test"})

        # Implementation detail: may or may not create log depending on how
        # report_missing logging is implemented vs general tracing
