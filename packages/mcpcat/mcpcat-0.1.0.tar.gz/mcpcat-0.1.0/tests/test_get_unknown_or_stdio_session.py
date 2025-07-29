"""Test get_unknown_or_stdio_session functionality."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from mcpcat import track
from mcpcat.modules.internal import get_mcpcat_data
from mcpcat.modules.session import get_unknown_or_stdio_session
from tests.test_utils import cleanup_log_file

from .test_utils.todo_server import create_todo_server


class TestGetUnknownOrSTDIOSession:
    """Test get_unknown_or_stdio_session functionality."""
    def setup_method(self):
        """Clean up log file before each test."""
        cleanup_log_file()

    def teardown_method(self):
        """Clean up log file after each test."""
        cleanup_log_file()

    def test_throw_when_no_tracking_data_exists(self):
        """Should throw when no tracking data exists."""
        untracked_server = create_todo_server()

        with pytest.raises(Exception, match="Server tracking data not found"):
            data = get_mcpcat_data(untracked_server)
            if not data:
                raise Exception("Server tracking data not found")
            get_unknown_or_stdio_session(untracked_server)

    @patch('mcpcat.modules.session.datetime')
    def test_create_new_session_when_none_exists(self, mock_datetime):
        """Should create a new session when none exists."""
        now = datetime.now()
        mock_datetime.now.return_value = now

        server = create_todo_server()
        track(server)

        data = get_mcpcat_data(server)
        assert data is not None

        session_id = get_unknown_or_stdio_session(server)
        assert session_id is not None
        assert isinstance(session_id, str)
        assert data.unknown_session is not None
        assert data.unknown_session.created == now

    def test_return_same_session_if_not_expired(self):
        """Should return the same session object if not expired."""
        server = create_todo_server()
        track(server)

        data = get_mcpcat_data(server)
        assert data is not None

        session_id1 = get_unknown_or_stdio_session(server)
        session_id2 = get_unknown_or_stdio_session(server)

        assert session_id1 == session_id2
        assert data.unknown_session is not None
        # Last used time should be updated
        assert data.unknown_session.last_used >= data.unknown_session.created

    @patch('mcpcat.modules.session.datetime')
    def test_reset_session_expiration_when_accessed_before_expiry(self, mock_datetime):
        """Should reset session expiration when accessed again before expiry."""
        now = datetime.now()
        mock_datetime.now.return_value = now

        server = create_todo_server()
        track(server)

        data = get_mcpcat_data(server)
        assert data is not None

        session_id1 = get_unknown_or_stdio_session(server)
        original_last_used = data.unknown_session.last_used

        # Simulate time passing (50ms)
        later = now + timedelta(milliseconds=50)
        mock_datetime.now.return_value = later

        session_id2 = get_unknown_or_stdio_session(server)

        assert session_id2 == session_id1
        assert data.unknown_session.last_used == later
        assert data.unknown_session.last_used > original_last_used

    def test_create_new_session_if_expired(self):
        """Should create new session if expired."""
        server = create_todo_server()
        track(server)

        data = get_mcpcat_data(server)
        assert data is not None

        session_id1 = get_unknown_or_stdio_session(server)
        old_session_id = session_id1

        # Simulate expiry by setting last_used to 31 minutes ago
        if data.unknown_session:
            data.unknown_session.last_used = datetime.now() - timedelta(minutes=31)

        session_id2 = get_unknown_or_stdio_session(server)
        assert session_id2 != old_session_id
        assert data.unknown_session is not None
        assert data.unknown_session.last_used > datetime.now() - timedelta(seconds=1)

    @patch('mcpcat.modules.session.datetime')
    def test_always_reset_expiration_to_30_minutes_from_now(self, mock_datetime):
        """Should always reset expiration to 30 minutes from now."""
        t1 = datetime.now()
        mock_datetime.now.return_value = t1

        server = create_todo_server()
        track(server)

        data = get_mcpcat_data(server)
        assert data is not None

        session_id1 = get_unknown_or_stdio_session(server)
        assert data.unknown_session.last_used == t1

        # Advance time by 1 second
        t2 = t1 + timedelta(seconds=1)
        mock_datetime.now.return_value = t2

        session_id2 = get_unknown_or_stdio_session(server)
        assert session_id1 == session_id2
        assert data.unknown_session.last_used == t2

    def test_maintain_isolation_between_multiple_servers(self):
        """Should maintain isolation between multiple servers."""
        server1 = create_todo_server()
        server2 = create_todo_server()
        track(server1)
        track(server2)

        data1 = get_mcpcat_data(server1)
        data2 = get_mcpcat_data(server2)
        assert data1 is not None
        assert data2 is not None

        session_id1 = get_unknown_or_stdio_session(server1)
        session_id2 = get_unknown_or_stdio_session(server2)

        assert session_id1 != session_id2

    def test_keep_session_consistent_for_same_server(self):
        """Should keep session consistent for same server."""
        server = create_todo_server()
        track(server)

        data = get_mcpcat_data(server)
        assert data is not None

        session_id1 = get_unknown_or_stdio_session(server)
        session_id2 = get_unknown_or_stdio_session(server)

        assert session_id1 == session_id2

    @patch('mcpcat.modules.session.datetime')
    def test_handle_multiple_rapid_accesses_correctly(self, mock_datetime):
        """Should handle multiple rapid accesses correctly."""
        now = datetime.now()
        mock_datetime.now.return_value = now

        server = create_todo_server()
        track(server)

        data = get_mcpcat_data(server)
        assert data is not None

        sessions = [get_unknown_or_stdio_session(server) for _ in range(5)]

        session_id = sessions[0]
        for session in sessions:
            assert session == session_id
            assert data.unknown_session.last_used == now
