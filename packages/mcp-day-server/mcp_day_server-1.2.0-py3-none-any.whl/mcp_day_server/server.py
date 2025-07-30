import time

from mcp.server import FastMCP

mcp = FastMCP(
    'rcloud-server-mcp-server',
    instructions="""
    # RongCloud IM Service MCP Server
    This server provides tools to interact with RongCloud services, focusing on user management, messaging, and group operations.
    """,
)

@mcp.tool(
    name='get_current_time_millis',
    description="Get the current time in milliseconds since Unix epoch (January 1, 1970 UTC).",
)
def get_current_time_millis()->int:
    """Get the current time in milliseconds since Unix epoch (January 1, 1970 UTC)."""
    return int(time.time() * 1000)




def main():
    print("sss")

    mcp.run()


if __name__ == '__main__':
    main()