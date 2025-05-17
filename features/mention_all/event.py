import logging
import telethon
from . import is_active
from bot import client

_logger = logging.getLogger("main")


@client.on(telethon.events.NewMessage(pattern=r"(?is).*@all.*"))
async def handler(event: telethon.events.NewMessage.Event):
    if not is_active():
        return

    chat = await event.get_chat()
    participants = await client.get_participants(chat)
    mention_list = []

    for user in participants:
        if not isinstance(user, telethon.types.User):
            continue
        if user.bot:
            continue
        if user.id == event.sender_id:
            continue
        if user.username:
            mention_list.append(f"@{user.username}")
        else:
            mention_list.append(f"[{user.first_name}](tg://user?id={user.id})")

    if mention_list:
        await event.reply(" ".join(mention_list))
        _logger.info(f"mention_all: Mentioned {len(mention_list)} users.")
