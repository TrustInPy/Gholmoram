import asyncio
import aiosqlite
from data.chats_data import CHAT_DATA_CACHE, insert_or_update_all_chats
from data.database import DATABASE_NAME, USER_DATA_CACHE, insert_or_update_all_users
from data.epic_game_data import FREE_GAMES_CACHE, insert_or_update_all_free_games, get_free_games_links


async def update_database_periodically():
    while True:
        if len(USER_DATA_CACHE) == 0 and len(CHAT_DATA_CACHE) == 0:
            await asyncio.sleep(20)
        else:
            try:
                conn = await aiosqlite.connect(DATABASE_NAME)
                await insert_or_update_all_users(conn, USER_DATA_CACHE)
                await insert_or_update_all_chats(conn, CHAT_DATA_CACHE)
                await insert_or_update_all_free_games(conn, FREE_GAMES_CACHE)
            except Exception as e:
                print(e)
            finally:
                if conn is not None:
                    await conn.close()
            await asyncio.sleep(20)


async def hour_task():
    try:
        await get_free_games_links()
        await asyncio.sleep(20)
    except Exception as e:
        print(e)


async def starter():
    asyncio.create_task(update_database_periodically())
    asyncio.create_task(hour_task())
