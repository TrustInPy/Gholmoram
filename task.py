import asyncio
import aiosqlite
from data.epic_game_data import get_free_games_links
from data.chats_data import CHAT_DATA_CACHE, insert_or_update_all_chats
from data.database import DATABASE_NAME, USER_DATA_CACHE, insert_or_update_all_users


async def update_database_periodically():
    while True:
        try:
            conn = await aiosqlite.connect(DATABASE_NAME)
            await insert_or_update_all_users(conn, USER_DATA_CACHE)
            await insert_or_update_all_chats(conn, CHAT_DATA_CACHE)
        except Exception as e:
            print(e)
        finally:
            if conn is not None:
                await conn.close()
        await asyncio.sleep(600)


async def tasks():
    while True:
        try:
            await get_free_games_links()
            print("Epic free games updated in database.")
            await asyncio.sleep(300)
        except Exception as e:
            print(e)


async def starter():
    asyncio.gather(update_database_periodically(), tasks())
