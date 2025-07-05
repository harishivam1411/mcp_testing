import asyncio
import nest_asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

"""
Make sure:
1. The server is running before running this script.
2. The server is configured to use SSE transport.
3. The server is listening on port 8000.

To run the server:
uv run server.py / python server.py

To run the file:
uv run client-sse.py / python client-sse.py
"""

nest_asyncio.apply()  # Needed to run interactive python

async def main():
    # Connect to the server using SSE
    async with sse_client("http://localhost:8000/sse") as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")
                print("*****-----*****")
            print()

            # Call our Weather tool
            result = await session.call_tool("get_alerts", arguments={"state":"CA"})
            print(f"The weather alerts are = \n{result.content[0].text}")


if __name__ == "__main__":
    print("Running the client-sse.py file")
    asyncio.run(main())
