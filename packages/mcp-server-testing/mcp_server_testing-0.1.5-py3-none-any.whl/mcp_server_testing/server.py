from fastmcp import FastMCP

mcp = FastMCP("MCP Test Server")

@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"
