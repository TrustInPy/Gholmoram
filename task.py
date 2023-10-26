import asyncio
import sqlite3
import aiosqlite
from bot import client
from data.epic_game_data import get_free_games_links, send_valid_links_to_chats
from data.database import DATABASE_NAME, USER_DATA_CACHE, insert_or_update_all_users


async def update_database_periodically():
    while True:
        try:
            conn = await aiosqlite.connect(DATABASE_NAME)
            await insert_or_update_all_users(conn, USER_DATA_CACHE)
        except sqlite3.OperationalError as e:
            print(f"Lost connection to the database: {e}")
            print("Attempting to reconnect...")
            try:
                conn = await aiosqlite.connect(DATABASE_NAME)
                print("Reconnected to the database.")
            except Exception as e:
                print(f"Failed to reconnect: {e}")
        except Exception as e:
            print(e)
        finally:
            await asyncio.sleep(600)


async def tasks():
    while True:
        try:
            await get_free_games_links()
            print("Epic free games updated in database.")
        except Exception as e:
            print(e)

        await asyncio.sleep(600)


async def epic_task():
    while True:
        try:
            await send_valid_links_to_chats(client, DATABASE_NAME)
            print("Free games task done.")
        except Exception as e:
            print(e)

        await asyncio.sleep(600)


async def starter():
    asyncio.gather(update_database_periodically(), tasks(), epic_task())
