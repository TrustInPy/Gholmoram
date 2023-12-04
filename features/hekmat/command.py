import re
import random
import requests
from bot import client
from telethon.sync import events
from features.start.buttons import keyboard


def hekmat(number=None):
    try:
        if number is None:
            number = random.randrange(1, 481)
        if number not in range(1, 481):
            return f"کلا 480 تا حکمت داریم بعد تو میگی {number} ؟! 🗿"

        url = f"https://alimaktab.ir/json/wisdom/?n={number}"
        response = requests.get(url)
        response_json = response.json()
        arabic = response_json["main"]
        farsi = response_json["ansarian"]
        hekmat = "حکمت " + str(number) + ": " + arabic + "\n\n" + farsi
        new_string = hekmat.replace("[", "").replace("]", "")

        def remove_html(text):
            clean = re.compile("<.*?>")
            return re.sub(clean, "", text)

        clean_text = remove_html(new_string)
        clean_text = clean_text.replace("&raquo;", "»")
        clean_text = clean_text.replace("&laquo;", "«")
        return clean_text
    except Exception as e:
        print("*** Can not get Hekmat ...")
        return "‼️ متاسفانه حکمت دریافت نشد !\n  دوباره تلاش کنید"


@client.on(
    events.NewMessage(func=lambda e: e.is_group or e.is_private, pattern="(?i)/hekmat")
)
async def handler(event):
    message_chat_id = event.chat_id
    command_parts = event.message.text.split(" ")
    try:
        number = None
        if len(command_parts) > 1:
            try:
                number = int(command_parts[1])
            except:
                await event.reply(f'‏"{command_parts[1]}" نامعتبر است 🫠')
                return
        text = hekmat(number)
        await client.delete_messages(message_chat_id, event._message_id)
        if not event.is_private:
            first_name = event.message.sender.first_name
            mention = f"[@{first_name}](tg://user?id={event.message.sender_id})"
            text = mention + "\n" + text
        await client.send_message(message_chat_id, text, buttons=keyboard)
    except:
        pass


@client.on(events.CallbackQuery(pattern="Hekmat"))
async def callback(event):
    message_chat_id = event.chat_id
    text = hekmat()
    if not event.is_private:
        first_name = event.sender.first_name
        mention = f"[@{first_name}](tg://user?id={event.sender_id})"
        text = mention + "\n" + text
    await event.answer("یک حکمت از نهج البلاغه")
    await client.send_message(message_chat_id, text, buttons=keyboard)
    await client.edit_message(message_chat_id, event._message_id, buttons=None)
