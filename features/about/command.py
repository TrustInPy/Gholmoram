from bot import *
from version import VERSION


@client.on(events.NewMessage(func=lambda e: e.is_group, pattern="(?i)/about"))
async def about(event):
    if event.chat_id in HOME:
        message_chat_id = event.chat_id

        try:
            about = f"""**🇮🇷 Gholmoram** \n✅ **v{VERSION}** \n📌 **AEDAN GAMING** \n👨🏻‍💻 {ADMIN_USERNAME} \n🖥 https://github.com/aedangaming
"""
            await client.send_message(message_chat_id, about)
        except Exception as e:
            print("About" + str(e))
    else:
        pass
