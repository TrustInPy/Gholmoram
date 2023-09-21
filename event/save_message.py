import aiosqlite
from telethon.sync import events
from bot import client, DATABASE_NAME


@client.on(events.NewMessage())
async def handler(event):
    user = await event.get_sender()
    user_id = user.id
    chat_id = event.chat_id
    message_id = event.id
    reply_to_message_id = event.reply_to_msg_id
    if event.message.forward:
        if event.message.forward.from_id:
            forward_from_user_id =  event.message.forward.from_id.user_id
        else:
            forward_from_user_id = event.message.forward.from_name
    else:
        forward_from_user_id = None


    if event.photo:
        if event.message.message:
            message_text = f"<Photo>\n {event.message.message}"
        else :
            message_text = "<Photo>"
            
    elif event.audio:
        if event.message.message:
            message_text = f"<Audio>\n {event.message.message}"
        else :
            message_text = "<Audio>"

    elif event.video:
        if event.message.message:
            message_text = f"<Video>\n {event.message.message}"
        else :
            message_text = "<Video>"

    elif event.document:
        if event.message.message:
            message_text = f"<Document ({event.document.mime_type})>\n {event.message.message}"
        else :
            message_text = f"<Document ({event.document.mime_type})>"

    else:
        message_text = event.raw_text


    try:
        conn = await aiosqlite.connect(DATABASE_NAME)
        cursor = await conn.cursor()
        await cursor.execute(
            """
            INSERT INTO messages (chat_id, user_id, message_id, message_text, reply_to_message_id, forward_from_user_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (chat_id, user_id, message_id, message_text, reply_to_message_id, forward_from_user_id)
        )
        await conn.commit()
        print("Message saved.")
        await conn.close()
    except aiosqlite.Error as e:
        print(f"Error saving message: {e}")

