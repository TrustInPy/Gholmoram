from bot import client
from version import VERSION
from telethon.sync import events
from telethon import functions, types
from features.start.buttons import keyboard

ADMIN = {
    "name": "Sina",
    "access_hash": -4572404436797027872,
    "user_id": 1465986382,
}


async def about():
    try:
        users = None
        try:
            users = await client(
                functions.users.GetUsersRequest(
                    [types.InputUser(ADMIN["user_id"], ADMIN["access_hash"])]
                )
            )
        except Exception as e:
            print(e)
            pass

        if users and len(users) > 0:
            about = (
                "**🇮🇷 Gholmoram** \n"
                + f"✅ **v{VERSION}** \n"
                + "📌 **AEDAN GAMING** \n"
                + f"👨🏻‍💻 [{ADMIN['name']}](tg://resolve/?domain={users[0].username})\n"
                + "🖥 [Github](https://github.com/aedangaming) \n"
                + "💬 [Discord](https://discord.gg/ZJVhgBCw3Q)"
            )
        else:
            about = (
                "**🇮🇷 Gholmoram** \n"
                + f"✅ **v{VERSION}** \n"
                + "📌 **AEDAN GAMING** \n"
                + f"👨🏻‍💻 {ADMIN['name']}\n"
                + "🖥 [Github](https://github.com/aedangaming) \n"
                + "💬 [Discord](https://discord.gg/ZJVhgBCw3Q)"
            )
        return about
    except Exception as e:
        print("*** Can not get About ...")
        return "‼️ متاسفانه درباره ما دریافت نشد !\n  دوباره تلاش کنید"


@client.on(
    events.NewMessage(func=lambda e: e.is_group or e.is_private, pattern="(?i)/about")
)
async def handler(event):
    message_chat_id = event.chat_id
    text = await about()
    try:
        await client.delete_messages(message_chat_id, event._message_id)
        if not event.is_private:
            first_name = event.message.sender.first_name
            mention = f"[@{first_name}](tg://user?id={event.message.sender_id})"
            text = mention + "\n" + text
    except:
        pass
    await client.send_message(message_chat_id, text, buttons=keyboard)


@client.on(events.CallbackQuery(pattern="About"))
async def callback(event):
    message_chat_id = event.chat_id
    text = await about()
    if not event.is_private:
        first_name = event.sender.first_name
        mention = f"[@{first_name}](tg://user?id={event.sender_id})"
        text = mention + "\n" + text
    await event.answer("درباره ما")
    await client.send_message(message_chat_id, text, buttons=keyboard)
    await client.edit_message(message_chat_id, event._message_id, buttons=None)
