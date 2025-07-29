"""Test context parameter integration functionality."""

import os
from pathlib import Path

import pytest

from mcpcat import track
from mcpcat.types import MCPCatOptions, UserData

from .test_utils import LOG_FILE, cleanup_log_file
from .test_utils.client import create_test_client
from .test_utils.todo_server import create_todo_server


class TestContextParameterIntegration:
    """Test context parameter integration functionality."""
    def setup_method(self):
        """Clean up log file before each test."""
        cleanup_log_file()

    def teardown_method(self):
        """Clean up log file after each test."""
        cleanup_log_file()

    @pytest.mark.asyncio
    async def test_work_with_identify_functionality(self):
        """Should work with identify functionality."""
        server = create_todo_server()

        async def identify_user(arguments, context) -> UserData:
            return {
                "userId": "test-user",
                "userData": {"name": "Test User"}
            }

        track(server, MCPCatOptions(
            enableToolCallContext=True,
            enableTracing=True,
            identify=identify_user
        ))

        # Simulate a tool call with context
        async with create_test_client(server) as client:
            await client.call_tool("add_todo", {
                "text": "Test todo",
                "context": "Testing with user identification"
            })

        assert os.path.exists(LOG_FILE)
        log_content = Path(LOG_FILE).read_text()
        assert "test-user" in log_content
        assert "Testing with user identification" in log_content

    @pytest.mark.asyncio
    async def test_handle_empty_context_string(self):
        """Should handle empty context string."""
        server = create_todo_server()
        track(server, MCPCatOptions(enableToolCallContext=True, enableTracing=True))

        # Simulate a tool call with empty context
        async with create_test_client(server) as client:
            await client.call_tool("add_todo", {
                "text": "Test todo",
                "context": ""  # Empty context
            })

        assert os.path.exists(LOG_FILE)
        log_content = Path(LOG_FILE).read_text()
        # Check that empty context is handled
        assert '"context": ""' in log_content  # Just ensure log exists, empty context is valid
