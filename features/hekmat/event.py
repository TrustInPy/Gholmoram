import aiohttp
import logging
import random
import re
import telethon
from . import is_active
from bot import client

_logger = logging.getLogger("main")


@client.on(telethon.events.NewMessage(pattern=r"(?i)/hekmat"))
async def handler(event):
    if not is_active():
        return

    number = None
    message_parts = event.message.text.split(" ")

    if len(message_parts) > 1:
        try:
            number = int(message_parts[1])
        except:
            pass

    try:
        text = await hekmat(number)
        await event.reply(text)
        _logger.info("features/hekmat: Sent a Hekmat.")
    except Exception as e:
        await event.reply(str(e))


async def hekmat(number=None):
    if number is None:
        number = random.randrange(1, 481)
    if number < 1:
        raise Exception("شماره حکمت ها از ۱ هست تا ۴۸۰ !")
    if number not in range(1, 481):
        raise Exception(f"کلا ۴۸۰ تا حکمت داریم بعد تو میگی {number} ؟! 🗿")

    try:
        url = f"https://alimaktab.ir/wp-json/content/v1/wisdom?n={number}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception()
                response_json = await resp.json()

        arabic = response_json["main"]
        farsi = response_json["translations"]["ansarian"]
        hekmat = "حکمت " + str(number) + ": " + arabic + "\n\n" + farsi
        new_string = hekmat.replace("[", "").replace("]", "")

        clean_text = remove_html(new_string)
        clean_text = clean_text.replace("&raquo;", "»")
        clean_text = clean_text.replace("&laquo;", "«")
        return clean_text
    except Exception as e:
        _logger.error(f"features/hekmat: Cannot get Hekmat number {number} Reason: {e}")
        raise Exception("متاسفانه حکمت دریافت نشد‼️")


def remove_html(text):
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)
