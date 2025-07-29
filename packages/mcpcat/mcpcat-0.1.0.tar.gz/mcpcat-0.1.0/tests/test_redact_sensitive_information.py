"""Test redact sensitive information functionality."""

import asyncio
import os
from pathlib import Path

import pytest

from mcpcat import track
from mcpcat.types import MCPCatOptions

from .test_utils import LOG_FILE, cleanup_log_file
from .test_utils.client import create_test_client
from .test_utils.todo_server import create_todo_server


class TestRedactSensitiveInformation:
    """Test redact sensitive information functionality."""
    def setup_method(self):
        """Clean up log file before each test."""
        cleanup_log_file()

    def teardown_method(self):
        """Clean up log file after each test."""
        cleanup_log_file()

    @pytest.mark.asyncio
    async def test_redact_context_when_function_provided(self):
        """Should redact context when redaction function is provided."""
        server = create_todo_server()

        async def redact_emails(text: str) -> str:
            """Simple redaction that replaces emails with [REDACTED]."""
            import re
            return re.sub(r'[\w.-]+@[\w.-]+\.\w+', '[REDACTED]', text)

        track(server, MCPCatOptions(
            enableTracing=True,
            enableToolCallContext=True,
            redactSensitiveInformation=redact_emails
        ))

        async with create_test_client(server) as client:
            await client.call_tool("add_todo", {
                "text": "Contact user@example.com",
                "context": "Need to email user@example.com about the project"
            })

        assert os.path.exists(LOG_FILE)
        log_content = Path(LOG_FILE).read_text()
        assert "[REDACTED]" in log_content
        assert "user@example.com" not in log_content

    @pytest.mark.asyncio
    async def test_handle_redaction_function_errors_gracefully(self):
        """Should handle redaction function errors gracefully."""
        server = create_todo_server()

        async def failing_redaction(text: str) -> str:
            """Redaction function that always fails."""
            raise Exception("Redaction failed")

        track(server, MCPCatOptions(
            enableTracing=True,
            enableToolCallContext=True,
            redactSensitiveInformation=failing_redaction
        ))

        async with create_test_client(server) as client:
            await client.call_tool("add_todo", {
                "text": "Sensitive data",
                "context": "Processing SSN 123-45-6789"
            })

        assert os.path.exists(LOG_FILE)
        log_content = Path(LOG_FILE).read_text()
        # Should log original content when redaction fails
        assert "123-45-6789" in log_content
        assert "Redaction failed" in log_content


    @pytest.mark.asyncio
    async def test_work_with_async_redaction_functions(self):
        """Should work with async redaction functions."""
        server = create_todo_server()

        async def async_redact_phones(text: str) -> str:
            """Async redaction that replaces phone numbers."""
            # Simulate async operation
            await asyncio.sleep(0.01)
            import re
            return re.sub(r'\d{3}-\d{3}-\d{4}', '[PHONE]', text)

        track(server, MCPCatOptions(
            enableTracing=True,
            enableToolCallContext=True,
            redactSensitiveInformation=async_redact_phones
        ))

        async with create_test_client(server) as client:
            await client.call_tool("add_todo", {
                "text": "Call customer",
                "context": "Customer phone is 555-123-4567"
            })

        assert os.path.exists(LOG_FILE)
        log_content = Path(LOG_FILE).read_text()
        assert "[PHONE]" in log_content
        assert "555-123-4567" not in log_content

    @pytest.mark.asyncio
    async def test_not_redact_when_passthrough_function(self):
        """Should not redact when redaction function is overridden with passthrough."""
        server = create_todo_server()

        async def passthrough_redaction(text: str) -> str:
            """Passthrough function to disable redaction."""
            return text

        track(server, MCPCatOptions(
            enableTracing=True,
            enableToolCallContext=True,
            redactSensitiveInformation=passthrough_redaction
        ))

        async with create_test_client(server) as client:
            await client.call_tool("add_todo", {
                "text": "Contact info",
                "context": "Email: user@example.com, Phone: 555-123-4567"
            })

        assert os.path.exists(LOG_FILE)
        log_content = Path(LOG_FILE).read_text()
        # Should contain original content when using passthrough function
        assert "Email: user@example.com, Phone: 555-123-4567" in log_content

    @pytest.mark.asyncio
    async def test_redact_context_in_tool_call_arguments(self):
        """Should redact context in tool call arguments."""
        server = create_todo_server()

        async def redact_credit_cards(text: str) -> str:
            """Redact credit card numbers."""
            import re
            return re.sub(r'\d{4}-\d{4}-\d{4}-\d{4}', '[CC]', text)

        track(server, MCPCatOptions(
            enableTracing=True,
            enableToolCallContext=True,
            redactSensitiveInformation=redact_credit_cards
        ))

        async with create_test_client(server) as client:
            await client.call_tool("add_todo", {
                "text": "Process payment",
                "context": "Card ending in 1234-5678-9012-3456"
            })

        assert os.path.exists(LOG_FILE)
        log_content = Path(LOG_FILE).read_text()
        assert "[CC]" in log_content
        assert "1234-5678-9012-3456" not in log_content
