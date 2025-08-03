import logging
import telethon
from . import is_active
from bot import client

_logger = logging.getLogger("main")


@client.on(telethon.events.NewMessage(pattern=r"(?i)/id"))
async def handle_new_message(event: telethon.events.NewMessage.Event):
    if not is_active():
        return

    message_text = event.message.message.strip()
    response = ""
    collected_ids_count = 0

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
            collected_ids_count += 1
    else:
        # Check for mentions in the message
        seen_ids = {}
        entity_was_mentioned = False
        mentioned_entities = event.message.entities
        if mentioned_entities:
            for entity in mentioned_entities:

                if isinstance(entity, telethon.types.MessageEntityMention):
                    # Mentioned by username
                    entity_was_mentioned = True
                    username = event.message.raw_text[
                        entity.offset + 1 : entity.offset + entity.length
                    ]
                    input_peer = await client.get_input_entity(username)
                    if isinstance(input_peer, telethon.types.InputPeerUser):
                        if seen_ids.get(input_peer.user_id):
                            continue
                        seen_ids[input_peer.user_id] = True
                        response += f"👤 {username} -> `{input_peer.user_id}`\n"
                        collected_ids_count += 1
                    elif isinstance(input_peer, telethon.types.InputPeerChat):
                        if seen_ids.get(input_peer.chat_id):
                            continue
                        seen_ids[input_peer.chat_id] = True
                        response += f"💬 {username} -> `{input_peer.chat_id}`\n"
                        collected_ids_count += 1
                    elif isinstance(input_peer, telethon.types.InputPeerChannel):
                        if seen_ids.get(input_peer.channel_id):
                            continue
                        seen_ids[input_peer.channel_id] = True
                        response += f"📢 {username} -> `{input_peer.channel_id}`\n"
                        collected_ids_count += 1
                    elif isinstance(input_peer, telethon.types.InputPeerSelf):
                        me = await client.get_me(input_peer=True)
                        if seen_ids.get(me.user_id):
                            continue
                        seen_ids[me.user_id] = True
                        response += f"🤖 {username} -> `{me.user_id}`\n"
                        collected_ids_count += 1

                elif isinstance(entity, telethon.types.MessageEntityMentionName):
                    # Mentioned by name (no username)
                    entity_was_mentioned = True
                    first_name = event.message.raw_text[
                        entity.offset : entity.offset + entity.length
                    ]
                    input_peer = await client.get_input_entity(entity.user_id)
                    if isinstance(input_peer, telethon.types.InputPeerUser):
                        if seen_ids.get(input_peer.user_id):
                            continue
                        seen_ids[input_peer.user_id] = True
                        response += f"👤 {first_name} -> `{input_peer.user_id}`\n"
                        collected_ids_count += 1

        if not entity_was_mentioned:
            # Check if this is a replied message and return id of the reference message sender
            if event.message.is_reply:
                ref_message = await client.get_messages(
                    event.chat, ids=event.message.reply_to.reply_to_msg_id
                )
                # Check if the reference message was forwarded
                forward = ref_message.forward
                if forward:
                    if forward.chat_id:
                        # Forward from channel/group
                        response += f"💬 {forward.chat.title} -> `{forward.chat_id}`\n"
                        collected_ids_count += 1
                    elif forward.sender:
                        # Forward from user
                        emoji = f"{"🤖" if forward.sender.bot else "👤"}"
                        response += f"{emoji} {forward.sender.first_name} -> `{forward.sender_id}`\n"
                        collected_ids_count += 1

                # Reference message sender
                emoji = f"{"🤖" if ref_message.sender.bot else "👤"}"
                response += f"{emoji} {ref_message.sender.first_name} -> `{ref_message.sender_id}`\n"
                collected_ids_count += 1
                entity_was_mentioned = True

        if not entity_was_mentioned:
            # Default to sender's ID if no mentions
            response = f"👤 User ID: `{event.sender_id}`\n"
            collected_ids_count += 1

    response += f"\n💬 This chat ID: `{event.chat_id}`"

    if response:
        await event.reply(response)
        _logger.info(
            f"features/id: Found id of {collected_ids_count} entities,"
            + f" Caller: {event.sender_id}"
        )
