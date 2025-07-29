"""Test MCP Version Compatibility."""


from mcpcat.modules.compatibility import is_compatible_server

from .test_utils.todo_server import create_todo_server


class TestMCPVersionCompatibility:
    """Test MCP Version Compatibility."""

    def test_compatible_with_currently_installed_mcp_version(self):
        """Should be compatible with currently installed MCP version."""
        # Create a new server instance
        server = create_todo_server()

        # Test compatibility using is_compatible_server
        result = is_compatible_server(server)
        assert result is True
