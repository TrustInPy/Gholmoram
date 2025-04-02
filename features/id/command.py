import telethon
from bot import client
from features.id import is_active


@client.on(telethon.events.NewMessage(pattern=r"(?i)/id$"))
async def handle_new_message(event: telethon.events.NewMessage.Event):
    if not is_active():
        return

    await event.reply(f"Your user ID: `{event.sender_id}`")
