import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():
    async with streamable_http_client(
        "http://127.0.0.1:8001/mcp"
    ) as (read_stream, write_stream):

        async with ClientSession(
            read_stream,
            write_stream
        ) as session:

            await session.initialize()

            result = await session.call_tool(
                "order_trends",
                {
                    "start_date": "2017-01-01",
                    "end_date": "2017-12-31",
                    "granularity": "month",
                },
            )

            print("Tool execution successful!")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())