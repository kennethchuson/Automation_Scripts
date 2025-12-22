# mcp_server.py
from mcp.server.fastmcp import FastMCP
from pathlib import Path
import datetime
import httpx
import math

# Base directory locked to where the script lives
BASE_DIR = Path(__file__).parent.resolve()

mcp = FastMCP("Enhanced Local MCP Server")

@mcp.tool()
def echo(message: str) -> str:
    """Echo back the provided message exactly."""
    return f"Echo: {message}"

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers and return the sum."""
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers and return the product."""
    return a * b

@mcp.tool()
def dot_mermsill(a: float, b: float, c: float) -> float:
    """Multiply three numbers and minius a number multiply by 2 and return the result."""
    return (a * b * c) - (a * 2) 



# IMPORTANT: No print() statements here — they break the JSON-RPC protocol
if __name__ == "__main__":
    mcp.run()