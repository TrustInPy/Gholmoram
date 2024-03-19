import aiosqlite
from telethon.sync import events, Button
from bot import client, DATABASE_NAME, ADMIN_ID

is_notification = None
selected_chats = []


@client.on(events.NewMessage(pattern="(?i)/notification"))
async def handler(event):
    global notification
    global selected_chats
    global chats
    global button_message
    connection = await aiosqlite.connect(DATABASE_NAME)
    cursor = await connection.cursor()
    await cursor.execute("SELECT chat_id, title FROM chats")
    result = await cursor.fetchall()
    chats = [(row[0], row[1]) for row in result]
    await connection.close()
    if event.sender_id == ADMIN_ID:

        try:
            is_notification = event.message.text.split(" ", 1)
            if len(is_notification) < 2:
                await client.send_message(event.chat_id, "متن پیام دریافت نشد 💤")
                return
            notification = is_notification[1]
            selected_chats = []
            buttons = [
                [Button.inline(chat[1], data=chat[0])]
                for chat in chats
                if chat not in selected_chats
            ]
            buttons.append([Button.inline("📨 ارسال", data="finish")])
            buttons.append([Button.inline("❌ حذف همه", data="deselect")])
            button_message = await client.send_message(
                event.chat_id,
                "🔅لطفا گروه های مورد نظر را انتخاب کنید: \n\nگروه ها: \n"
                + "\n".join([chat[1] for chat in selected_chats]),
                buttons=buttons,
            )
        except Exception as e:
            print("Error in /notification" + str(e))


@client.on(events.CallbackQuery)
async def callback_handler(event):
    global notification
    global selected_chats
    if event.sender_id == ADMIN_ID:

        selection = event.data.decode("utf-8")
        if selection == "finish":

            for chat in selected_chats:
                await client.send_message(chat[0], notification)
            try:
                await client.delete_messages(event.chat_id, button_message)
            except Exception as e:
                pass
            notification = None
            selected_chats = []
            return
        elif selection == "deselect":
            try:
                await client.delete_messages(event.chat_id, button_message)
            except Exception as e:
                pass
            selected_chats = []
            notification = None
            return
        else:
            try:
                selection = int(selection)
            except ValueError:
                pass
            try:
                selected_chat = next(
                    (chat for chat in chats if chat[0] == selection), None
                )
            except Exception as e:
                await client.send_message(event.chat_id, "دوباره سعی کنید ⛔")
                await client.delete_messages(event.chat_id, event.message_id)
                return
            if selected_chat is not None:
                selected_chats.append(selected_chat)

        await event.edit(
            "🔅لطفا گروه های مورد نظر را انتخاب کنید: \n\nگروه ها: \n"
            + "\n".join([chat[1] for chat in selected_chats]),
            buttons=[
                [Button.inline(chat[1], data=chat[0])]
                for chat in chats
                if chat not in selected_chats
            ]
            + [
                [Button.inline("📨 ارسال", data="finish")],
                [Button.inline("❌ حذف همه", data="deselect")],
            ],
        )
