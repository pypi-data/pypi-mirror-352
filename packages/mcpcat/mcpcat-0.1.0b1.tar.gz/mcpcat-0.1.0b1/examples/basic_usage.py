"""Basic usage example for MCPCat with FastMCP."""

from fastmcp import FastMCP

from mcpcat import MCPCatOptions, track

# Create a FastMCP server
mcp = FastMCP("example-server")


# Define some tools
@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"Weather in {city}: Sunny, 72°F"


# Enable MCPCat tracking with custom options
options = MCPCatOptions(
    enableToolCallContext=True,
    enableTracing=True,
    enableReportMissing=True,
    identify=lambda ctx: {
        "sessionId": "session-123",
        "userId": "user-456"
    } if ctx else None
)

# Track the server
track(mcp, options)

# Run the server
if __name__ == "__main__":
    mcp.run()
