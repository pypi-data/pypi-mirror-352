"""Test options handling."""


from mcpcat import track
from mcpcat.types import MCPCatOptions
from tests.test_utils import cleanup_log_file

from .test_utils.todo_server import create_todo_server


class TestOptionsHandling:
    """Test options handling."""
    def setup_method(self):
        """Clean up log file before each test."""
        cleanup_log_file()

    def teardown_method(self):
        """Clean up log file after each test."""
        cleanup_log_file()

    def test_accept_default_options(self):
        """Should accept default options."""
        server = create_todo_server()
        tracked_server = track(server)

        assert tracked_server is server

    def test_handle_partial_options(self):
        """Should handle partial options."""
        server = create_todo_server()
        tracked_server = track(server, MCPCatOptions(enableReportMissing=False))

        assert tracked_server is server

    def test_handle_empty_options_object(self):
        """Should handle empty options object."""
        server = create_todo_server()
        tracked_server = track(server, MCPCatOptions())

        assert tracked_server is server
