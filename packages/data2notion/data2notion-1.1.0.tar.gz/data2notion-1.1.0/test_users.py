#!/usr/bin/env python3
from notion_client import AsyncClient
import os
import asyncio
from notion_client.helpers import async_collect_paginated_api
from pprint import pprint

notion = AsyncClient(auth=os.environ["NOTION_TOKEN"])


async def list_users():
    list_users_response = await notion.users.list()
    pprint(list_users_response)


async def list_pages_single():
    list_pages = await notion.databases.query(
        database_id="0aac15e4791443b6af27f9c58b461d93"
    )
    pprint(list_pages)
    print(type(list_pages))


async def list_pages():
    list_pages = await async_collect_paginated_api(
        notion.databases.query, database_id="0aac15e4791443b6af27f9c58b461d93"
    )
    pprint(list_pages)


async def read_db_info():
    db_info = await notion.databases.retrieve(
        database_id="0aac15e4791443b6af27f9c58b461d93"
    )


if __name__ == "__main__":
    asyncio.run(read_db_info())
