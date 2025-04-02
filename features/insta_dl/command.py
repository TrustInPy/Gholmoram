import aiohttp
import logging
import re
import os
import uuid
import shutil
import telethon
from bot import client
from features.insta_dl import is_active

_logger = logging.getLogger("main")

SIGNATURE = "\n\n----------------------------------------------\n 🔻 @Gholmoram"


@client.on(telethon.events.NewMessage())
async def handler(event: telethon.events.NewMessage.Event):
    if not is_active():
        return

    chat = event.chat_id
    url = event.message.raw_text
    if not re.match(r"^https?://(www\.)?instagram\.com/.+$", url):
        return
    try:
        status_message = await client.send_message(
            event.chat_id, "در حال جستجو\n-------------------------"
        )
        cobalt_url = "http://127.0.0.1:3400/"
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        data = {"url": f"{url}"}

        response_json = None
        async with aiohttp.ClientSession() as session:
            async with session.post(cobalt_url, headers=headers, json=data) as resp:
                if resp.status != 200:
                    await event.reply("خطا API")
                    return
                response_json = await resp.json()

        media_url = response_json.get("url")
        filename = response_json.get("filename")

        if not media_url or not filename:
            await event.reply("خطا در دیتای بازگشتی درخواست")
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(media_url) as resp:
                if resp.status != 200:
                    await event.reply("دریافت رسانه با خطا مواجه شد")
                    return

                unique_id = str(uuid.uuid4())
                temp_dir = f"temp/insta_dl/{unique_id}"
                temp_file_path = f"temp/insta_dl/{unique_id}/{filename}"
                os.makedirs(temp_dir)

                await client.edit_message(
                    status_message, "شروع دانلود\n-------------------------"
                )

                with open(temp_file_path, "wb") as file:
                    async for chunk in resp.content.iter_chunked(8192):
                        file.write(chunk)

        await client.edit_message(status_message, "در حال ارسال فایل... 🔰")
        await client.send_file(
            chat,
            temp_file_path,
            caption=SIGNATURE,
            reply_to=event.message.id,
        )
        try:
            await client.delete_messages(chat, status_message)
        except:
            pass

    except Exception as e:
        _logger.error(f"Instagram - Error downloading Instagram media: {str(e)}")
        await event.reply("خطا API")
    finally:
        await client.delete_messages(event.chat_id, status_message)
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
