from bot import client
from telethon.sync import events
from .buttons import keyboard


@client.on(
    events.NewMessage(func=lambda e: e.is_group or e.is_private, pattern="(?i)/start")
)
async def start(event):
    await client.send_message(event.chat_id, "👑 **Gholmoram**", buttons=keyboard)
