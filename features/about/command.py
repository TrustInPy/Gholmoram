from bot import *
from version import VERSION
from telethon.sync import events


@client.on(
    events.NewMessage(func=lambda e: e.is_group or e.is_private, pattern="(?i)/about")
)
async def about(event):
    message_chat_id = event.chat_id
    try:
        about = f"**🇮🇷 Gholmoram** \n✅ **v{VERSION}** \n📌 **AEDAN GAMING** \n👨🏻‍💻 {ADMIN_USERNAME} \n🖥 [Github](https://github.com/aedangaming) \n💬 [Discord](https://discord.gg/ZJVhgBCw3Q)"
        await client.send_message(message_chat_id, about)
    except Exception as e:
        print("About" + str(e))
