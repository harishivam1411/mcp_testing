import asyncio
import nest_asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

"""
To run the file:
uv run client-stdio.py / python client-stdio.py
"""

nest_asyncio.apply()  # Needed to run interactive python

async def main():
    # Define server parameters
    params = StdioServerParameters(
        command="python",  # The command to run your server
        args=["server.py", "stdio"],  # Arguments to the command
    )

    # Connect to the server
    async with stdio_client(params) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            # Initialize the connection (remove duplicate)
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")
                print("*****-----*****")
            print()

            # Call our Weather Tool
            result = await session.call_tool("get_alerts", arguments={"state":"CA"})
            print(f"The weather alerts are = \n{result.content[0].text}")


if __name__ == "__main__":
    print("Running the client-stdio.py file")
    asyncio.run(main())