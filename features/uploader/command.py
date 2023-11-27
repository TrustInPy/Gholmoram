import aiohttp
import os
import re
import requests
import shutil
import uuid
from bot import client
from telethon import events


def is_url(s):
    pattern = re.compile(
        "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )
    if pattern.match(s):
        return True
    return False


@client.on(events.NewMessage(pattern="(?i)/upload"))
async def callback(event):
    try:
        command_parts = event.message.text.split(" ")
        if len(command_parts) < 2:
            await event.reply("لینک ندادی که 😩")
            return

        url = command_parts[1]
        chat = event.chat_id

        if not is_url(url):
            await event.reply("لینک شما نامعتبر است. متاسفانه ☺️")
            return

        local_filename = url.split("/")[-1].split("?")[0]
        unique_id = str(uuid.uuid4())
        temp_dir = f"tmp/{unique_id}"
        temp_file_path = f"tmp/{unique_id}/{local_filename}"

        written_bytes = 0
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if not r.headers.get("Content-length"):
                    await event.reply("لینکت ته نداره که... 😩")
                    return
                if int(r.headers["Content-length"]) > 2000000000:
                    await event.reply("حجم فایل شما بیش از 2 گیگابایت است. 🥺")
                    return

                try:
                    os.makedirs(temp_dir)
                except:
                    pass

                if not os.path.exists(temp_dir):
                    await event.reply("خطایی پیش اومد، بعدا امتحان کن")
                    return

                with open(temp_file_path, "wb") as f:
                    while True:
                        chunk = await r.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        written_bytes = written_bytes + len(chunk)
                        if written_bytes > 2000000000:
                            await event.reply("حجم فایل شما بیش از 2 گیگابایت است. 🥺")
                            return
            await client.send_file(chat, temp_file_path, reply_to=event.message.id)
    except Exception as e:
        print("Error in upload: " + str(e))
    finally:
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
