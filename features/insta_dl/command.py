import re
import os
import uuid
import requests
from telethon.sync import events
from bot import client


SIGNATURE = "\n\n----------------------------------------------\n 🔻 @Gholmoram"


@client.on(events.NewMessage(pattern="(?i)/instadl"))
async def callback(event):
    await client.send_message(
        event.chat_id, "توی آپدیت جدید دیگه نیازی به دستور /instadl نیست ✌"
    )


@client.on(events.NewMessage())
async def callback(event):
    chat = event.chat_id
    url = event.message.raw_text
    if re.match(r"^https?://(www\.)?instagram\.com/.+$", url):
        try:
            status_message = await client.send_message(
                event.chat_id, "در حال جستجو\n-------------------------"
            )
            copilot_url = "http://127.0.0.1:3400/"
            headers = {"Accept": "application/json", "Content-Type": "application/json"}
            data = {"url": f"{url}"}

            response = requests.post(copilot_url, headers=headers, json=data)

            if response.status_code == 200:
                media_url = response.json().get("url")
                filename = response.json().get("filename")

                if media_url and filename:
                    media_response = requests.get(media_url, stream=True)

                    if media_response.status_code == 200:
                        unique_id = str(uuid.uuid4())
                        temp_dir = f"tmp/{unique_id}"
                        temp_file_path = f"tmp/{unique_id}/{filename}"

                        try:
                            os.makedirs(temp_dir)
                        except:
                            pass

                        if not os.path.exists(temp_dir):
                            await event.reply("خطایی پیش اومد، بعدا امتحان کن")
                            return

                        await client.edit_message(
                            status_message, "شروع دانلود\n-------------------------"
                        )

                        with open(temp_file_path, "wb") as file:
                            for chunk in media_response.iter_content(chunk_size=8192):
                                file.write(chunk)

                        await client.edit_message(
                            status_message, "در حال ارسال فایل... 🔰"
                        )
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

                    else:
                        await event.reply("دریافت رسانه با خطا مواجه شد")
                        return
                else:
                    await event.reply("خطا در دیتای بازگشتی درخواست")
                    return
            else:
                await event.reply("خطا API")
                return
        except Exception as e:
            print(f"Instagram - Error downloading Instagram media: {str(e)}")
        finally:
            await client.delete_messages(event.chat_id, status_message)
    else:
        return
