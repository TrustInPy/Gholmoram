import datetime
from bot import client
from telethon.sync import events
from data.database import update_cache, USER_DATA_CACHE
from telethon.tl.functions.users import GetFullUserRequest


@client.on(events.NewMessage(func=lambda e: e.is_private))
async def handler(event):
    user_id = event.chat_id
    username = event.chat.username
    first_name = event.chat.first_name
    last_name = event.chat.last_name
    last_interaction = datetime.datetime.now()
    access_hash = event.chat.access_hash
    full = await client(GetFullUserRequest(user_id))
    bio = full.full_user.about
    is_bot = event.chat.bot

    user_data = {
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "last_interaction": last_interaction,
        "access_hash": access_hash,
        "bio": bio,
        "is_bot": is_bot,
    }

    if user_id not in USER_DATA_CACHE:
        user_data["date_joined"] = datetime.datetime.now()

    await update_cache(user_data)

    print("Done")
