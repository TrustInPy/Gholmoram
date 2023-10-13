import datetime
from bot import client
from telethon.sync import events
from data.database import update_cache, USER_DATA_CACHE
from telethon.tl.functions.users import GetFullUserRequest


@client.on(events.NewMessage(func=lambda e: e.is_group))
async def handler(event):
    user = await event.get_sender()
    user_id = user.id

    # Check if the user already exists in the database
    if user_id not in USER_DATA_CACHE:
        full = await client(GetFullUserRequest(user_id))
        user_data = {
            "user_id": user_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "last_interaction": None,
            "access_hash": user.access_hash,
            "bio": full.full_user.about,
            "is_bot": user.bot,
            "date_joined": datetime.datetime.now(),
        }
        await update_cache(user_data)
    else:
        # If the user already exists, update other user data fields
        full = await client(GetFullUserRequest(user_id))
        existing_user_data = USER_DATA_CACHE[user_id]
        existing_user_data["username"] = user.username
        existing_user_data["first_name"] = user.first_name
        existing_user_data["last_name"] = user.last_name
        existing_user_data["access_hash"] = user.access_hash
        existing_user_data["bio"] = full.full_user.about
        existing_user_data["is_bot"] = user.bot

    print("Done")
