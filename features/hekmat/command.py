import re
import random
import requests
from bot import *

@client.on(events.NewMessage(func=lambda e: e.is_group, pattern='(?i)/hekmat'))
async def hekmat(event):
    if event.chat_id in HOME:
        message_chat_id = event.chat_id

        try:
            number = random.randrange(1, 481)
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

            await client.send_message(message_chat_id, clean_text)

        except Exception as e:
            print("Hafez" + str(e))
    else:
        pass


@client.on(events.NewMessage(func=lambda e: e.is_private, pattern='(?i)/hekmat'))
async def hekmat(event):
    # if event.chat_id in HOME:
        message_chat_id = event.chat_id

        try:
            number = random.randrange(1, 481)
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

            await client.send_message(message_chat_id, clean_text)

        except Exception as e:
            print("Hafez" + str(e))
    # else:
    #     pass