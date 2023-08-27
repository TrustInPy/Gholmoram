from bot import client
from version import VERSION
from telethon.sync import events
from telethon import functions, types

ADMIN = {
    "name": "Sina",
    "access_hash": -4572404436797027872,
    "user_id": 1465986382,
}


@client.on(
    events.NewMessage(func=lambda e: e.is_group or e.is_private, pattern="(?i)/about")
)
async def about(event):
    message_chat_id = event.chat_id
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
        await client.send_message(message_chat_id, about)
    except Exception as e:
        print("About " + str(e))
