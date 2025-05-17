import telethon
from . import is_active
from bot import client
from version import VERSION


@client.on(telethon.events.NewMessage(pattern=r"(?i)/about"))
async def handle_new_message(event: telethon.events.NewMessage.Event):
    if not is_active():
        return

    await event.reply(about_text())


def about_text():
    about = (
        "**🇮🇷 Gholmoram** \n"
        + f"✅ **v{VERSION}** \n"
        + "📌 by **AEDAN GAMING** \n"
        + "🖥 [Github](https://github.com/aedangaming) \n"
        + "💬 [Discord](https://discord.gg/ZJVhgBCw3Q)"
    )
    return about
