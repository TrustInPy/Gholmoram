import os
import re
import requests
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
        url = event.message.text.split(" ")[1]
        chat = event.chat_id
        if not is_url(url):
            await event.reply("لینک شما نامعتبر است. متاسفانه ☺️")
            return

        local_filename = url.split("/")[-1].split("?")[0]
        written_bytes = 0
        with requests.get(url, stream=True) as r:
            if not r.headers.get("Content-length"):
                await event.reply("لینکت ته نداره که... 😩")
                return
            if int(r.headers["Content-length"]) > 2000000000:
                await event.reply("حجم فایل شما بیش از 2 گیگابایت است. 🥺")
                return

            r.raise_for_status()
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    written_bytes = written_bytes + 8192
                    if written_bytes > 2000000000:
                        await event.reply("حجم فایل شما بیش از 2 گیگابایت است. 🥺")
                        return
        await client.send_file(chat, local_filename, reply_to=event.message.id)
    except Exception as e:
        print("Error in upload: " + str(e))
    finally:
        try:
            os.remove(local_filename)
        except:
            pass
