# server.py
import os
from mcp.server.fastmcp import FastMCP
from mcp.types import Resource, TextContent

mcp = FastMCP("SDK-MCP-Demo", host="0.0.0.0", port=8000, json_response=True)  # json_response for easy debugging

@mcp.tool()
def list_files(directory: str = ".") -> str:
    """List files in a directory."""
    try:
        files = os.listdir(directory)
        return "\n".join(files)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def read_file(filepath: str) -> str:
    """Read contents of a text file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> Resource:
    """Get a personalized greeting (resource for context loading)."""
    return Resource(
        uri=f"greeting://{name}",
        mimeType="text/plain",
        content=[TextContent(text=f"Hello, {name}!")]
    )

if __name__ == "__main__":
    mcp.run(transport="http")