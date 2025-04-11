import aiohttp
import logging
import telethon
from bot import client
from features.hafez import is_active

_logger = logging.getLogger("main")


@client.on(telethon.events.NewMessage(pattern=r"(?i)/hafez"))
async def handler(event):
    if not is_active():
        return

    message_chat_id = event.chat_id
    text = await hafez()
    try:
        await client.delete_messages(message_chat_id, event._message_id)
        if not event.is_private:
            first_name = event.message.sender.first_name
            mention = f"[@{first_name}](tg://user?id={event.message.sender_id})"
            text = mention + "\n" + text
    except:
        pass
    await client.send_message(message_chat_id, text)


async def hafez():
    try:
        url = "https://c.ganjoor.net/beyt-xml.php?n=1&a=1&p=2"
        xml = None
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception()
                xml = await resp.text()
        m1 = xml.split("<m1>")[1].split("</m1>")[0]
        m2 = xml.split("<m2>")[1].split("</m2>")[0]
        poet = xml.split("<poet>")[1].split("</poet>")[0]
        total_poem = xml.split("<url>")[1].split("</url>")[0]
        up = "🖊️"
        poem = f"{m1}\n{m2}\n\n{up} [{poet}]({total_poem})"
        return poem

    except Exception as e:
        return "‼️ متاسفانه شعر دریافت نشد !\n  دوباره تلاش کنید"
