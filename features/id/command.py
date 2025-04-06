import telethon
from bot import client
from features.id import is_active


@client.on(telethon.events.NewMessage(pattern=r"(?i)/id"))
async def handle_new_message(event: telethon.events.NewMessage.Event):
    if not is_active():
        return

    message_text = event.message.message.strip()
    response = ""
    seen_user_ids = {}

    if message_text.lower().startswith("/id all"):
        # Get all users in the chat
        participants = await client.get_participants(event.chat_id)
        for user in participants:
            if user.username:
                response += (
                    f"{"🤖" if user.bot else "👤"} {user.username} -> `{user.id}`\n"
                )
            else:
                response += (
                    f"{"🤖" if user.bot else "👤"} {user.first_name} -> `{user.id}`\n"
                )
    else:
        # Check for mentions in the message
        mentioned_entities = event.message.entities
        if mentioned_entities:
            for entity in mentioned_entities:
                if isinstance(entity, telethon.types.MessageEntityMention):
                    username = event.message.raw_text[
                        entity.offset : entity.offset + entity.length
                    ]
                    user = await client.get_entity(username)
                    if seen_user_ids.get(user.id):
                        continue
                    seen_user_ids[user.id] = True
                    response += f"{"🤖" if user.bot else "👤"} {user.first_name} -> `{user.id}`\n"
                elif isinstance(entity, telethon.types.MessageEntityMentionName):
                    user = await client.get_entity(entity.user_id)
                    if seen_user_ids.get(user.id):
                        continue
                    seen_user_ids[user.id] = True
                    if user.username:
                        response += f"{"🤖" if user.bot else "👤"} {user.username} -> `{user.id}`\n"
                    else:
                        response += f"{"🤖" if user.bot else "👤"} {user.first_name} -> `{user.id}`\n"
        else:
            # Default to sender's ID if no mentions
            response = f"👤 User ID: `{event.sender_id}`"

    response += f"\n💬 Chat ID: `{event.chat_id}`"

    if response:
        await event.reply(response)
