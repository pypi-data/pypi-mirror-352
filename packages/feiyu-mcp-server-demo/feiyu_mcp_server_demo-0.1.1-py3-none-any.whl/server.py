# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """执行加法操作"""
    return a + b

@mcp.tool()
def now() -> str:
    """获取当前时间"""
    from datetime import datetime
    return datetime.now().isoformat()

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """获得一个问候语"""
    return f"Hello, {name}!"
