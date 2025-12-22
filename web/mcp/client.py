# client.py
import asyncio
import httpx
from mcp.client.http import ClientHTTPTransport
from mcp import ClientSession

async def main():
    async with httpx.AsyncClient() as http_client:
        transport = ClientHTTPTransport(
            "http://localhost:8000/mcp",  # Server endpoint
            http_client=http_client
        )
        async with ClientSession(transport) as session:
            # Initialize (handshake)
            await session.initialize()
            print("Initialized. Capabilities:", session.server_info)

            # List tools
            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])

            # Call a tool: list_files
            result = await session.call_tool(
                name="list_files",
                arguments={"directory": "."}
            )
            print("list_files result:", result.content)

            # Call a tool: read_file
            result = await session.call_tool(
                name="read_file",
                arguments={"filepath": "server.py"}  # Assuming run from same dir
            )
            print("read_file result:", result.content[:200] + "..." if len(result.content) > 200 else result.content)

            # Fetch a resource
            resource = await session.read_resource(uri="greeting://World")
            print("Greeting resource:", resource.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())