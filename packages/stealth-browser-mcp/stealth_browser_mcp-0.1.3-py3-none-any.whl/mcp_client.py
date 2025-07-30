from fastmcp import Client


async def main():
    # Connect via SSE
    # async with Client("playwright_mcp_server.py") as client:
    async with Client("http://localhost:3000/mcp") as client:
        tools = await client.list_tools()
        print("Available tools:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")

        # result = await client.call_tool("add", {"a": 5, "b": 3})
        # print(f"Result: {result.text}")
        result = await client.call_tool(
            "browser_navigate", {"url": "https://example.com"}
        )
        print(f"Result: {result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
