"""Test track() function."""


from mcpcat import track
from mcpcat.types import MCPCatOptions
from tests.test_utils import cleanup_log_file

from .test_utils.todo_server import create_todo_server


class TestTrack:
    """Test track() function."""
    def setup_method(self):
        """Clean up log file before each test."""
        cleanup_log_file()

    def teardown_method(self):
        """Clean up log file after each test."""
        cleanup_log_file()

    def test_return_same_server_instance(self):
        """Should return the same server instance."""
        server = create_todo_server()
        tracked_server = track(server)

        assert tracked_server is server
        assert hasattr(tracked_server, 'tool')

    def test_work_with_custom_options(self):
        """Should work with custom options."""
        server = create_todo_server()
        tracked_server = track(server, MCPCatOptions(
            enableReportMissing=False,
            enableTracing=False,
        ))

        assert tracked_server is server
