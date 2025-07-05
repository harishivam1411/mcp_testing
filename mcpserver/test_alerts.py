import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

"""
To run the file:
uv run test_alerts.py / python test_alerts.py
"""

async def test_alerts():
    params = StdioServerParameters(
        command="python",
        args=["server.py", "stdio"],
    )

    async with stdio_client(params) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()

            # Test different states
            states = ["CA", "NY", "FL", "TX", "WA"]

            for state in states:
                print(f"\n=== Testing alerts for {state} ===")
                result = await session.call_tool("get_alerts", arguments={"state": state})
                print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(test_alerts())