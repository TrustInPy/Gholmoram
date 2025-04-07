import telethon
from bot import client
from features.id import is_active


@client.on(telethon.events.NewMessage(pattern=r"(?i)/id"))
async def handle_new_message(event: telethon.events.NewMessage.Event):
    if not is_active():
        return

    message_text = event.message.message.strip()
    response = ""

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
        seen_ids = {}
        user_was_mentioned = False
        mentioned_entities = event.message.entities
        if mentioned_entities:
            for entity in mentioned_entities:

                if isinstance(entity, telethon.types.MessageEntityMention):
                    user_was_mentioned = True
                    username = event.message.raw_text[
                        entity.offset + 1 : entity.offset + entity.length
                    ]
                    input_peer = await client.get_input_entity(username)
                    if isinstance(input_peer, telethon.types.InputPeerUser):
                        if seen_ids.get(input_peer.user_id):
                            continue
                        seen_ids[input_peer.user_id] = True
                        response += f"👤 {username} -> `{input_peer.user_id}`\n"
                    elif isinstance(input_peer, telethon.types.InputPeerChat):
                        if seen_ids.get(input_peer.chat_id):
                            continue
                        seen_ids[input_peer.chat_id] = True
                        response += f"💬 {username} -> `{input_peer.chat_id}`\n"
                    elif isinstance(input_peer, telethon.types.InputPeerChannel):
                        if seen_ids.get(input_peer.channel_id):
                            continue
                        seen_ids[input_peer.channel_id] = True
                        response += f"📢 {username} -> `{input_peer.channel_id}`\n"

                elif isinstance(entity, telethon.types.MessageEntityMentionName):
                    user_was_mentioned = True
                    first_name = event.message.raw_text[
                        entity.offset : entity.offset + entity.length
                    ]
                    input_peer = await client.get_input_entity(entity.user_id)
                    if isinstance(input_peer, telethon.types.InputPeerUser):
                        if seen_ids.get(input_peer.user_id):
                            continue
                        seen_ids[input_peer.user_id] = True
                        response += f"👤 {first_name} -> `{input_peer.user_id}`\n"

        if not user_was_mentioned:
            # Default to sender's ID if no mentions
            response = f"👤 User ID: `{event.sender_id}`\n"

    response += f"\n💬 This chat ID: `{event.chat_id}`"

    if response:
        await event.reply(response)
