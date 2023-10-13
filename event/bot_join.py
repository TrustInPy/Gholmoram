import datetime
import aiosqlite
from bot import client, DATABASE_NAME
from telethon.sync import events, types
from data.chats_data import update_chat_cache
from data.database import update_cache, USER_DATA_CACHE
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetFullChannelRequest


@client.on(events.ChatAction)
async def handler(event):
    # Check if the event is about the bot joining the group
    if event.action_message is not None and isinstance(
        event.action_message.action,
        (
            types.MessageActionChatJoinedByLink,
            types.MessageActionChatAddUser,
        ),
    ):
        me = await client.get_me()
        BOT_ID = me.id
        # Check if the bot is the user that joined
        if event.user_id == BOT_ID:
            try:
                participants = await client.get_participants(event.chat_id)

                for user in participants:
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

                print("start of chat data collection...")
                # Get chat details
                chat = await client.get_entity(event.chat_id)
                full_chat = await client(GetFullChannelRequest(chat.id))
                chat_data = {
                    "chat_id": chat.id,
                    "access_hash": chat.access_hash,
                    "title": chat.title,
                    # "type": chat.type,
                    "members_count": full_chat.full_chat.participants_count,
                    "last_interaction": datetime.datetime.now(),
                    "description": full_chat.full_chat.about,
                    "link": full_chat.full_chat.exported_invite.link
                    if full_chat.full_chat.exported_invite
                    else None,
                }

                conn = await aiosqlite.connect(DATABASE_NAME)
                await update_chat_cache(conn, chat_data)
                await conn.close()

                print("Done")
            except Exception as e:
                print(e)
