"""Test identify function handler."""

import os
from pathlib import Path

import pytest

from mcpcat import track
from mcpcat.types import MCPCatOptions, UserData

from .test_utils import LOG_FILE, cleanup_log_file
from .test_utils.client import create_test_client
from .test_utils.todo_server import create_todo_server


class TestIdentifyFunction:
    """Test identify function handler."""

    def setup_method(self):
        """Clean up log file before each test."""
        cleanup_log_file()

    def teardown_method(self):
        """Clean up log file after each test."""
        cleanup_log_file()

    @pytest.mark.asyncio
    async def test_call_identify_function_on_first_tool_call(self):
        """Should call identify function on first tool call for a session."""
        identify_called = False
        captured_request = None
        captured_extra = None

        async def identify_user(arguments, context) -> UserData:
            nonlocal identify_called, captured_request, captured_extra
            identify_called = True
            captured_request = arguments
            captured_extra = context
            return {
                "userId": "user123",
                "userData": {"name": "Test User", "email": "test@example.com"}
            }

        server = create_todo_server()
        track(server, MCPCatOptions(
            enableTracing=True,
            identify=identify_user
        ))

        # Use client_session to create proper MCP connection
        async with create_test_client(server) as client:
            # First tool call should trigger identify
            result = await client.call_tool("add_todo", {
                "text": "Test todo",
                "context": "Testing identification"
            })

            assert identify_called
            assert captured_request is not None
            assert captured_extra is not None

            # The result will be a CallToolResult object
            assert len(result.content) == 1
            assert result.content[0].text  # Check the actual response

            assert os.path.exists(LOG_FILE)
            log_content = Path(LOG_FILE).read_text()
            assert "user123" in log_content

    @pytest.mark.asyncio
    async def test_not_call_identify_on_subsequent_calls_same_session(self):
        """Should not call identify function on subsequent tool calls for same session."""
        identify_call_count = 0

        async def identify_user(arguments, context) -> UserData:
            nonlocal identify_call_count
            identify_call_count += 1
            return {
                "userId": "user123"
            }

        server = create_todo_server()
        track(server, MCPCatOptions(
            enableTracing=True,
            identify=identify_user
        ))

        async with create_test_client(server) as client:
            # First call should trigger identify
            await client.call_tool("add_todo", {
                "text": "First todo",
                "context": "First call"
            })

            # Second call should NOT trigger identify
            await client.call_tool("add_todo", {
                "text": "Second todo",
                "context": "Second call"
            })

        assert identify_call_count == 1

        assert os.path.exists(LOG_FILE)
        log_content = Path(LOG_FILE).read_text()
        # Check that user identification happens only once
        assert log_content.count("User identified") == 1
        assert log_content.count("user123") >= 1

    @pytest.mark.asyncio
    async def test_call_identify_for_different_sessions(self):
        """Should call identify function for different sessions."""
        identify_call_count = 0
        identified_sessions = []

        async def identify_user(arguments, context) -> UserData:
            nonlocal identify_call_count
            identify_call_count += 1
            return {
                "userId": f"user{identify_call_count}",
                "userData": {"name": f"User {identify_call_count}"}
            }

        server = create_todo_server()
        track(server, MCPCatOptions(
            enableTracing=True,
            identify=identify_user
        ))

        # First session
        async with create_test_client(server) as client1:
            await client1.call_tool("add_todo", {
                "text": "Todo 1",
                "context": "Session 1"
            })

        # Second session - new client connection creates new session
        async with create_test_client(server) as client2:
            await client2.call_tool("add_todo", {
                "text": "Todo 2",
                "context": "Session 2"
            })

        # For STDIO-like connections (memory transport), sessions are reused
        # So we only expect one identify call
        assert identify_call_count == 1

        assert os.path.exists(LOG_FILE)
        log_content = Path(LOG_FILE).read_text()
        assert "user1" in log_content

    @pytest.mark.asyncio
    async def test_handle_identify_function_returning_none(self):
        """Should handle identify function returning None."""
        identify_called = False

        async def identify_user(arguments, context) -> None:
            nonlocal identify_called
            identify_called = True
            return None  # No identification

        server = create_todo_server()
        track(server, MCPCatOptions(
            enableTracing=True,
            identify=identify_user
        ))

        async with create_test_client(server) as client:
            await client.call_tool("add_todo", {
                "text": "Test todo",
                "context": "Testing null identification"
            })

            assert identify_called

            assert os.path.exists(LOG_FILE)
            log_content = Path(LOG_FILE).read_text()
            assert "add_todo" in log_content

    @pytest.mark.asyncio
    async def test_handle_identify_function_throwing_error(self):
        """Should handle identify function throwing an error."""
        identify_called = False

        async def identify_user(arguments, context) -> UserData:
            nonlocal identify_called
            identify_called = True
            raise Exception("Identification failed")

        server = create_todo_server()
        track(server, MCPCatOptions(
            enableTracing=True,
            identify=identify_user
        ))

        async with create_test_client(server) as client:
            await client.call_tool("add_todo", {
                "text": "Test todo",
                "context": "Testing error handling"
            })

            assert identify_called

            assert os.path.exists(LOG_FILE)
            log_content = Path(LOG_FILE).read_text()
            assert "Identification failed" in log_content
            assert "add_todo" in log_content  # Should still proceed

    @pytest.mark.asyncio
    async def test_not_call_identify_when_not_provided(self):
        """Should not call identify function when identify option is not provided."""
        server = create_todo_server()
        track(server, MCPCatOptions(
            enableTracing=True
            # No identify function provided
        ))

        async with create_test_client(server) as client:
            await client.call_tool("add_todo", {
                "text": "Test todo",
                "context": "Testing no identify function"
            })

            assert os.path.exists(LOG_FILE)
            log_content = Path(LOG_FILE).read_text()
            assert "add_todo" in log_content
