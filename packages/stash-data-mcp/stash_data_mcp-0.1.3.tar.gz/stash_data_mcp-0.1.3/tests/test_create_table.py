from stash_data_mcp.server import mcp


async def test():
    tools = await mcp.list_tools()
    for tool in tools:
        if "drop_table_traveling_dogs" == tool.name:
            await mcp.call_tool("drop_table_traveling_dogs", {})

    await mcp.call_tool("create_table", {
        "table_name": "traveling_dogs",
        "columns": {
            "id": "integer",
            "name": "string",
            "country": "string",
            "owner": "string"
        },
        "partition_keys": ["id"]
    })


if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
