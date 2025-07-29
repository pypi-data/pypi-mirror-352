"""Test that mcpcat.track preserves existing tools and only adds report_missing."""

import pytest

from mcpcat import track
from mcpcat.types import MCPCatOptions

from .test_utils.client import create_test_client
from .test_utils.todo_server import create_todo_server


class TestPreserveExistingTools:
    """Test that existing tools are preserved when tracking."""

    async def test_track_preserves_all_existing_tools(self):
        """Should preserve all existing tools and only add report_missing."""
        # Create server with existing tools
        server = create_todo_server()
        
        # Get original tools before tracking
        async with create_test_client(server) as client:
            result = await client.list_tools()
            original_tools = result.tools
            original_tool_names = {tool.name for tool in original_tools}
        
        # Track the server
        tracked_server = track(server)
        
        # Get tools after tracking
        async with create_test_client(tracked_server) as client:
            result = await client.list_tools()
            tracked_tools = result.tools
            tracked_tool_names = {tool.name for tool in tracked_tools}
        
        # Verify all original tools are preserved
        assert original_tool_names.issubset(tracked_tool_names), "Original tools should be preserved"
        
        # Verify only report_missing was added
        added_tools = tracked_tool_names - original_tool_names
        assert added_tools == {"report_missing"}, "Only report_missing should be added"
        
        # Verify the exact count
        assert len(tracked_tools) == len(original_tools) + 1, "Should have exactly one more tool"
        
        # Verify original tools are still present
        assert "add_todo" in tracked_tool_names
        assert "list_todos" in tracked_tool_names
        assert "complete_todo" in tracked_tool_names

    async def test_track_without_report_missing_preserves_exact_tools(self):
        """Should preserve exact tool list when report_missing is disabled."""
        # Create server with existing tools
        server = create_todo_server()
        
        # Get original tools before tracking
        async with create_test_client(server) as client:
            result = await client.list_tools()
            original_tools = result.tools
            original_tool_names = {tool.name for tool in original_tools}
        
        # Track the server with report_missing disabled
        tracked_server = track(server, MCPCatOptions(enableReportMissing=False))
        
        # Get tools after tracking
        async with create_test_client(tracked_server) as client:
            result = await client.list_tools()
            tracked_tools = result.tools
            tracked_tool_names = {tool.name for tool in tracked_tools}
        
        # Verify tool lists are identical
        assert tracked_tool_names == original_tool_names, "Tool names should be identical"
        assert len(tracked_tools) == len(original_tools), "Tool count should be identical"

    async def test_track_with_context_modifies_existing_tools_but_preserves_them(self):
        """Should modify existing tools to add context but preserve all of them."""
        # Create server with existing tools
        server = create_todo_server()
        
        # Get original tools before tracking
        async with create_test_client(server) as client:
            result = await client.list_tools()
            original_tools = result.tools
            original_tool_names = {tool.name for tool in original_tools}
        
        # Track the server with context enabled
        tracked_server = track(server, MCPCatOptions(enableToolCallContext=True))
        
        # Get tools after tracking
        async with create_test_client(tracked_server) as client:
            result = await client.list_tools()
            tracked_tools = result.tools
        
        # Find modified tools (excluding report_missing)
        for tool in tracked_tools:
            if tool.name in original_tool_names:
                # Verify context was added to schema
                assert "context" in tool.inputSchema["properties"], f"Context should be added to {tool.name}"
                assert "context" in tool.inputSchema["required"], f"Context should be required for {tool.name}"
            elif tool.name == "report_missing":
                # Verify report_missing doesn't have context parameter
                assert "context" not in tool.inputSchema["properties"], "report_missing should not have context"
        
        # Verify all original tools are still present
        tracked_tool_names = {tool.name for tool in tracked_tools}
        assert original_tool_names.issubset(tracked_tool_names), "All original tools should be preserved"

    async def test_multiple_track_calls_do_not_duplicate_tools(self):
        """Should not duplicate tools when track is called multiple times."""
        # Create server with existing tools
        server = create_todo_server()
        
        # Track the server multiple times
        track(server)
        track(server)  # Should be a no-op
        track(server)  # Should be a no-op
        
        # Get tools after multiple track calls
        async with create_test_client(server) as client:
            result = await client.list_tools()
            tools = result.tools
            tool_names = [tool.name for tool in tools]
        
        # Count occurrences of each tool
        tool_counts = {}
        for name in tool_names:
            tool_counts[name] = tool_counts.get(name, 0) + 1
        
        # Verify no duplicates
        for name, count in tool_counts.items():
            assert count == 1, f"Tool {name} should appear exactly once, but appears {count} times"
        
        # Verify expected tools are present
        assert "add_todo" in tool_names
        assert "list_todos" in tool_names
        assert "complete_todo" in tool_names
        assert "report_missing" in tool_names
        assert len(tools) == 4, "Should have exactly 4 tools"