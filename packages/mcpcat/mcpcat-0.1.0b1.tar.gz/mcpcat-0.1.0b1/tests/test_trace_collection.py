"""Test trace collection functionality."""


from mcpcat import track
from tests.test_utils import cleanup_log_file

from .test_utils.todo_server import create_todo_server


class TestTraceCollection:
    """Test trace collection functionality."""
    def setup_method(self):
        """Clean up log file before each test."""
        cleanup_log_file()

    def teardown_method(self):
        """Clean up log file after each test."""
        cleanup_log_file()

    def test_work_with_tracked_servers(self):
        """Should work with tracked servers."""
        server = create_todo_server()
        tracked_server = track(server)

        assert tracked_server is server

    def test_maintain_server_functionality(self):
        """Should maintain server functionality."""
        server = create_todo_server()
        tracked_server = track(server)

        assert hasattr(tracked_server, 'tool')
        assert tracked_server is server
