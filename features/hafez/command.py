import requests
from bot import client
from telethon.sync import events
from features.start.buttons import keyboard


def hafez():
    try:
        url = "https://c.ganjoor.net/beyt-xml.php?n=1&a=1&p=2"
        response = requests.get(url)
        xml = response.content
        m1 = xml.split(b"<m1>")[1].split(b"</m1>")[0].decode("utf-8")
        m2 = xml.split(b"<m2>")[1].split(b"</m2>")[0].decode("utf-8")
        poet = xml.split(b"<poet>")[1].split(b"</poet>")[0].decode("utf-8")
        total_poem = xml.split(b"<url>")[1].split(b"</url>")[0].decode("utf-8")
        up = "🖊️"
        poem = f"{m1}\n{m2}\n\n{up} [{poet}]({total_poem})"
        return poem

    except Exception as e:
        print("*** Can not get Hafez ...")
        return "‼️ متاسفانه شعر دریافت نشد !\n  دوباره تلاش کنید"


@client.on(
    events.NewMessage(func=lambda e: e.is_group or e.is_private, pattern="(?i)/hafez")
)
async def handler(event):
    message_chat_id = event.chat_id
    text = hafez()
    try:
        await client.delete_messages(message_chat_id, event._message_id)
        if not event.is_private:
            first_name = event.message.sender.first_name
            mention = f"[@{first_name}](tg://user?id={event.message.sender_id})"
            text = mention + "\n" + text
    except:
        pass
    await client.send_message(message_chat_id, text)


@client.on(events.CallbackQuery(pattern="Hafez"))
async def callback(event):
    message_chat_id = event.chat_id
    text = hafez()
    if not event.is_private:
        first_name = event.sender.first_name
        mention = f"[@{first_name}](tg://user?id={event.sender_id})"
        text = mention + "\n" + text
    await event.answer("یک بیت از حافظ")
    await client.edit_message(message_chat_id, event._message_id, buttons=None)
    await client.send_message(message_chat_id, text, buttons=keyboard)
