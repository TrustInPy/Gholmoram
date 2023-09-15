import asyncio
import aiosqlite
from data.database import DATABASE_NAME, USER_DATA_CACHE, insert_or_update_all_users


async def update_database_periodically():
    while True:
        if len(USER_DATA_CACHE) == 0:
            await asyncio.sleep(40)
        else:
            try:
                conn = await aiosqlite.connect(DATABASE_NAME)
                await insert_or_update_all_users(conn, USER_DATA_CACHE)
                await conn.close()
                await asyncio.sleep(40)
            except Exception as e:
                print(e)


async def starter():
    asyncio.create_task(update_database_periodically())
