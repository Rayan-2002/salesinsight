import asyncio

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


server_params = StdioServerParameters(
    command="mcp",
    args=["run", "server.py"],
    env=None,
)


async def run():
    # Start the server and open communication streams
    async with stdio_client(server_params) as (read, write):

        # Create an MCP session over these streams
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Read a resource
            print("READING RESOURCE")
            resource = await session.read_resource("greeting://Rayan")

            for item in resource.contents:
                if isinstance(item, types.TextResourceContents):
                    print(item.text)

            # Call a tool
            print("CALLING A TOOL")
            result = await session.call_tool(
                "add",
                arguments={"a": 1, "b": 2},
            )

            for item in result.content:
                if isinstance(item, types.TextContent):
                    print(item.text)


if __name__ == "__main__":
    asyncio.run(run())