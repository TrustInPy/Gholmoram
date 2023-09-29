import aiosqlite
from telethon.sync import events
from bot import client, DATABASE_NAME
from datetime import datetime


@client.on(events.NewMessage(pattern="(?i)/epic"))
async def handler(event):
    try:
        conn = await aiosqlite.connect(DATABASE_NAME)

        cursor = await conn.cursor()
        current_date = datetime.now()
        query = f"""
            SELECT * FROM free_games
            WHERE end_date >= ?
            """
        await cursor.execute(query, (current_date,))
        free_games = await cursor.fetchall()
        await conn.close()

        for game in free_games:
            game_name = game[1]
            end_date = datetime.strptime(game[2], "%Y-%m-%d %H:%M:%S")
            game_link = game[3]

            end_date_str = end_date.strftime("%Y-%m-%d %H:%M")

            message = (
                f"💎 **{game_name}** is free\n"
                f"⏳ until **{end_date_str}**\n"
                f"----------------------------------------\n"
                f"👇🏻Get it here: {game_link}\n"
                f"----------------------------------------\n"
            )
            await client.send_message(event.chat_id, message)

    except Exception as e:
        print("Failed to get free games from database.\n" + str(e))
        await client.send_message(event.chat_id, "خطا در دریافت لینک‌ها ⚠️")
