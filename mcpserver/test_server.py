import asyncio
import nest_asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

nest_asyncio.apply()

async def test_comprehensive():
    """Test both weather tools with various inputs."""
    params = StdioServerParameters(
        command="python",
        args=["server.py", "stdio"],
    )

    async with stdio_client(params) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()

            print("=== MCP Weather Server Test ===\n")

            # Test 1: List available tools
            print("1. Available Tools:")
            tools_result = await session.list_tools()
            for tool in tools_result.tools:
                print(f"   - {tool.name}: {tool.description}")
                print("*****-----*****")
            print()

            # Test 2: Test alerts for multiple states
            print("2. Testing Weather Alerts:")
            states = ["CA", "NY", "FL", "TX", "WA"]
            for state in states:
                print(f"\n   Testing alerts for {state}:")
                try:
                    result = await session.call_tool("get_alerts", arguments={"state": state})
                    response = result.content[0].text
                    if "No active alerts" in response:
                        print(f"   ✓ No alerts for {state}")
                    else:
                        print(f"   ✓ Found alerts for {state}")
                        print(f"   Preview: {response[:100]}...")
                except Exception as e:
                    print(f"   ✗ Error for {state}: {e}")

            # Test 3: Test forecasts for different locations
            print("\n3. Testing Weather Forecasts:")
            locations = [
                {"name": "San Francisco", "lat": 37.7749, "lon": -122.4194},
                {"name": "New York", "lat": 40.7128, "lon": -74.0060},
                {"name": "Miami", "lat": 25.7617, "lon": -80.1918},
            ]

            for location in locations:
                print(f"\n   Testing forecast for {location['name']}:")
                try:
                    result = await session.call_tool(
                        "get_forecast",
                        arguments={"latitude": location['lat'], "longitude": location['lon']}
                    )
                    response = result.content[0].text
                    print(f"   ✓ Got forecast for {location['name']}")
                    print(f"   Preview: {response[:100]}...")
                except Exception as e:
                    print(f"   ✗ Error for {location['name']}: {e}")

            # Test 4: Test error handling
            print("\n4. Testing Error Handling:")

            # Invalid state code
            try:
                result = await session.call_tool("get_alerts", arguments={"state": "INVALID"})
                print(f"  Alerts - {result.content[0].text}")
                print("   ✓ Invalid state handled correctly")
            except Exception as e:
                print(f"   ✗ Invalid state error: {e}")

            # Invalid coordinates
            try:
                result = await session.call_tool("get_forecast", arguments={"latitude": 999, "longitude": 999})
                print(f"  Forecast - {result.content[0].text}")
                print("   ✓ Invalid coordinates handled correctly")
            except Exception as e:
                print(f"   ✗ Invalid coordinates error: {e}")

            print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_comprehensive())