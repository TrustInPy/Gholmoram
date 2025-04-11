import aiohttp
import html
import logging
import telethon
from bot import client
from features.hafez import is_active

_logger = logging.getLogger("main")


@client.on(telethon.events.NewMessage(pattern=r"(?i)/hafez"))
async def handler(event):
    if not is_active():
        return

    text = await hafez()
    await event.reply(text)
    _logger.info("features/hafez: Sent a Hafez poem.")


async def hafez():
    try:
        url = "https://c.ganjoor.net/beyt-xml.php?n=1&a=1&p=2"
        xml = None
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception()
                xml = await resp.read()

        xml = html.unescape(xml.decode("utf-8"))
        m1 = xml.split("<m1>")[1].split("</m1>")[0]
        m2 = xml.split("<m2>")[1].split("</m2>")[0]
        poet = xml.split("<poet>")[1].split("</poet>")[0]
        poem_url = xml.split("<url>")[1].split("</url>")[0]
        pen_emoji = "🖊️"
        return f"{m1}\n{m2}\n\n{pen_emoji} [{poet}]({poem_url})"

    except Exception as e:
        return "‼️ متاسفانه شعر دریافت نشد !\n  دوباره تلاش کنید"
