# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP(
    name="add",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8080,  # only used for SSE transport (set this to any port)
)


# Add an addition tool
@mcp.tool()
def add(a: int, b: int):
    """To implement a song using 2 numbers a,b"""
    return a + b




if __name__ == "__main__":
    # Start the server
    mcp.run(transport="stdio")