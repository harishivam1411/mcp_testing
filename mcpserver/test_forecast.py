import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

"""
To run the file:
uv run test_forecast.py / python test_forecast.py
"""

async def test_forecast():
    params = StdioServerParameters(
        command="python",
        args=["server.py", "stdio"],
    )

    async with stdio_client(params) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()

            # Test different locations
            locations = [
                {"name": "San Francisco", "lat": 37.7749, "lon": -122.4194},
                {"name": "New York", "lat": 40.7128, "lon": -74.0060},
                {"name": "Miami", "lat": 25.7617, "lon": -80.1918},
            ]

            for location in locations:
                print(f"\n=== Testing forecast for {location['name']} ===")
                result = await session.call_tool(
                    "get_forecast",
                    arguments={"latitude": location['lat'], "longitude": location['lon']}
                )
                print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(test_forecast())