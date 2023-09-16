from bot import client
from telethon.sync import events
from data.epic_game_data import FREE_GAMES_CACHE


@client.on(events.NewMessage(pattern="(?i)/epic"))
async def handler(event):
    for game_name, game_data in FREE_GAMES_CACHE.items():
        end_date = game_data["end_date"]
        game_link = game_data["url"]

        message = f"{game_name} is free until {end_date}. Get it here: {game_link}"
        await client.send_message(event.chat_id, message)