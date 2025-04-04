import aiohttp
import logging
import re
import os
import uuid
import shutil
import telethon
import aiohttp_socks
from bot import client
from envs import INSTADL_COBALT_API_URL
from features.insta_dl import is_active
from features.proxies import proxy_str_list
from yarl import URL

_logger = logging.getLogger("main")

SIGNATURE = "----------------------------------------------\n 🔻 @Gholmoram"


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
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        data = {"url": url}

        response_json = None
        async with aiohttp.ClientSession() as session:
            async with session.post(
                INSTADL_COBALT_API_URL, headers=headers, json=data
            ) as resp:
                if resp.status != 200:
                    await event.reply("خطا API")
                    return
                response_json = await resp.json()

        media_url = response_json.get("url")
        filename = response_json.get("filename")

        if not media_url or not filename:
            await event.reply("خطا در دیتای بازگشتی درخواست")
            return

        await client.edit_message(
            status_message, "شروع دانلود\n-------------------------"
        )
        temp_file_path, temp_dir = await download_and_save(media_url, filename)
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
        _logger.error(f"insta_dl: Error processing Instagram link: {str(e)}")
        await event.reply("خطا API")
    finally:
        await client.delete_messages(event.chat_id, status_message)
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


async def download_and_save(url: str, filename: str):
    try:
        url = URL(url, encoded=True)
        # Try downloading without a proxy first
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status >= 200 and resp.status < 300:
                    return await save_file(resp, filename)

    except Exception as e:
        _logger.warning(f"insta_dl: Error downloading file using no proxy")
        # If download fails, try with each proxy
        for proxy in proxy_str_list:
            try:
                if proxy.startswith("socks5://"):
                    connector = aiohttp_socks.ProxyConnector.from_url(proxy)
                    async with aiohttp.ClientSession(connector=connector) as session:
                        async with session.get(url) as resp:
                            if resp.status >= 200 and resp.status < 300:
                                return await save_file(resp, filename)
                            else:
                                raise Exception()
                else:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, proxy=proxy) as resp:
                            if resp.status >= 200 and resp.status < 300:
                                return await save_file(resp, filename)
                            else:
                                raise Exception()
            except:
                continue  # Try the next proxy
        _logger.error(f"insta_dl: Error downloading file: {str(e)}")
        return None, None


async def save_file(resp, filename):
    unique_id = str(uuid.uuid4())
    temp_dir = f"temp/insta_dl/{unique_id}"
    temp_file_path = f"temp/insta_dl/{unique_id}/{filename}"
    os.makedirs(temp_dir)
    with open(temp_file_path, "wb") as file:
        async for chunk in resp.content.iter_chunked(8192):
            file.write(chunk)
    return temp_file_path, temp_dir
