import requests
from bot import *
from telethon.sync import events

@client.on(events.NewMessage(func=lambda e: e.is_group, pattern='(?i)/hafez'))
async def hafez(event):
    if event.chat_id in HOME:
        message_chat_id = event.chat_id

        try:
            url = "https://c.ganjoor.net/beyt-xml.php?n=1&a=1&p=2"
            response = requests.get(url)
            xml = response.content
            m1 = xml.split(b"<m1>")[1].split(b"</m1>")[0].decode("utf-8")
            m2 = xml.split(b"<m2>")[1].split(b"</m2>")[0].decode("utf-8")
            poet = xml.split(b"<poet>")[1].split(b"</poet>")[0].decode("utf-8")
            up = "🖊️"
            poem = f"{m1}\n{m2}\n\n{up} {poet}"
            await client.send_message(message_chat_id, poem)
        except Exception as e:
            print("Hafez" + str(e))
    else:
        pass


@client.on(events.NewMessage(func=lambda e: e.is_private, pattern='(?i)/hafez'))
async def hafez(event):
    message_chat_id = event.chat_id
    
    try:
        url = "https://c.ganjoor.net/beyt-xml.php?n=1&a=1&p=2"
        response = requests.get(url)
        xml = response.content
        m1 = xml.split(b"<m1>")[1].split(b"</m1>")[0].decode("utf-8")
        m2 = xml.split(b"<m2>")[1].split(b"</m2>")[0].decode("utf-8")
        poet = xml.split(b"<poet>")[1].split(b"</poet>")[0].decode("utf-8")
        up = "🖊️"
        poem = f"{m1}\n{m2}\n\n{up} {poet}"
        await client.send_message(message_chat_id, poem)
    except Exception as e:
        print("Hafez" + str(e))
