from bot import client, ADMIN_ID
from telethon.sync import events


@client.on(events.NewMessage(func=lambda e: e.is_group, pattern="(?i)/members"))
async def handler(event):
    message_chat_id = event.chat_id
    user = event.message.sender_id
    if user == ADMIN_ID:
        try:
            text = ""
            async for user in client.iter_participants(message_chat_id):
                str_user_id = str(user.id)
                user_hash = str(user.access_hash)
                text = (
                    text
                    + f"[@{user.username}](tg://user?id={str_user_id}) "
                    + str_user_id
                    + "\n"
                    + user_hash
                    + "\n\n"
                )
            await client.send_message(message_chat_id, text)
            print(text)
        except Exception as e:
            print("Members" + str(e))
    else:
        print(f"Not user ({user}) tried to run /members in ({message_chat_id})")
        pass
