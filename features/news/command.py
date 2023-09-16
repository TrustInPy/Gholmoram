import requests
from bot import client, proxies
from telethon.sync import events
from .buttons import news_keyboard
from features.start.buttons import keyboard


@client.on(
    events.NewMessage(func=lambda e: e.is_group or e.is_private, pattern="(?i)/news")
)
async def news(event):
    await client.send_message(
        event.chat_id, "🌐 **دسته‌بندی اخبار**", buttons=news_keyboard
    )


@client.on(events.CallbackQuery(pattern="Day"))
async def callback(event):
    message_chat_id = event.chat_id
    max_length = 30
    try:
        url = "https://www.farsnews.ir/rss/topnews"
        response = requests.get(url, proxies)
        xml_data = response.content.decode("utf-8")
        item_tags = xml_data.split("<item>")[1:]
        khabar = ""
        for item_tag in item_tags:
            title = item_tag.split("<title>")[1].split("</title>")[0]
            if len(title) > max_length:
                title = title[:max_length] + "..."
            else:
                pass

            link = item_tag.split("<link>")[1].split("</link>")[0]
            khabar = khabar + f"🔅 [{title}]({link})\n"
        khabar = (
            "📌 ‏**اخبار برتر روز:**\n"
            + khabar
            + "\n🌐 [Farsnews](https://www.farsnews.ir)"
        )
        await event.answer("اخبار برتر روز")
        await client.send_message(
            message_chat_id, khabar, buttons=news_keyboard, link_preview=False
        )
        await client.edit_message(message_chat_id, event._message_id, buttons=None)

    except Exception as e:
        print("khabar " + str(e))


@client.on(events.CallbackQuery(pattern="Politic"))
async def callback(event):
    message_chat_id = event.chat_id
    max_length = 30
    try:
        url = "https://www.farsnews.ir/rss/politics/topnews"
        response = requests.get(url, proxies)
        xml_data = response.content.decode("utf-8")
        item_tags = xml_data.split("<item>")[1:]
        khabar = ""
        for item_tag in item_tags:
            title = item_tag.split("<title>")[1].split("</title>")[0]
            if len(title) > max_length:
                title = title[:max_length] + "..."
            else:
                pass

            link = item_tag.split("<link>")[1].split("</link>")[0]
            khabar = khabar + f"🔅 [{title}]({link})\n "
        khabar = (
            "📌 ‏**برترین اخبار سیاسی روز:**\n"
            + khabar
            + "\n🌐 [Farsnews](https://www.farsnews.ir)"
        )
        await event.answer("اخبار سیاسی")
        await client.send_message(
            message_chat_id, khabar, buttons=news_keyboard, link_preview=False
        )
        await client.edit_message(message_chat_id, event._message_id, buttons=None)

    except Exception as e:
        print("khabar " + str(e))


@client.on(events.CallbackQuery(pattern="Sport"))
async def callback(event):
    message_chat_id = event.chat_id
    max_length = 30
    try:
        url = "https://www.farsnews.ir/rss/sports/topnews"
        response = requests.get(url, proxies)
        xml_data = response.content.decode("utf-8")
        item_tags = xml_data.split("<item>")[1:]
        khabar = ""
        for item_tag in item_tags:
            title = item_tag.split("<title>")[1].split("</title>")[0]
            if len(title) > max_length:
                title = title[:max_length] + "..."
            else:
                pass

            link = item_tag.split("<link>")[1].split("</link>")[0]
            khabar = khabar + f"🔅 [{title}]({link})\n "
        khabar = (
            "📌 ‏**برترین اخبار ورزشی روز:**\n"
            + khabar
            + "\n🌐 [Farsnews](https://www.farsnews.ir)"
        )
        await event.answer("اخبار ورزشی")
        await client.send_message(
            message_chat_id, khabar, buttons=news_keyboard, link_preview=False
        )
        await client.edit_message(message_chat_id, event._message_id, buttons=None)

    except Exception as e:
        print("khabar " + str(e))


@client.on(events.CallbackQuery(pattern="Economy"))
async def callback(event):
    message_chat_id = event.chat_id
    max_length = 30
    try:
        url = "https://www.farsnews.ir/rss/economy/topnews"
        response = requests.get(url, proxies)
        xml_data = response.content.decode("utf-8")
        item_tags = xml_data.split("<item>")[1:]
        khabar = ""
        for item_tag in item_tags:
            title = item_tag.split("<title>")[1].split("</title>")[0]
            if len(title) > max_length:
                title = title[:max_length] + "..."
            else:
                pass

            link = item_tag.split("<link>")[1].split("</link>")[0]
            khabar = khabar + f"🔅 [{title}]({link})\n "
        khabar = (
            "📌 ‏**برترین اخبار اقتصادی روز:**\n"
            + khabar
            + "\n🌐 [Farsnews](https://www.farsnews.ir)"
        )
        await event.answer("اخبار اقتصادی")
        await client.send_message(
            message_chat_id, khabar, buttons=news_keyboard, link_preview=False
        )
        await client.edit_message(message_chat_id, event._message_id, buttons=None)

    except Exception as e:
        print("khabar " + str(e))


@client.on(events.CallbackQuery(pattern="Calture"))
async def callback(event):
    message_chat_id = event.chat_id
    max_length = 30
    try:
        url = "https://www.farsnews.ir/rss/culture/topnews"
        response = requests.get(url, proxies)
        xml_data = response.content.decode("utf-8")
        item_tags = xml_data.split("<item>")[1:]
        khabar = ""
        for item_tag in item_tags:
            title = item_tag.split("<title>")[1].split("</title>")[0]
            if len(title) > max_length:
                title = title[:max_length] + "..."
            else:
                pass

            link = item_tag.split("<link>")[1].split("</link>")[0]
            khabar = khabar + f"🔅 [{title}]({link})\n "
        khabar = (
            "📌 ‏**برترین اخبار فرهنگی وهنری روز:**\n"
            + khabar
            + "\n🌐 [Farsnews](https://www.farsnews.ir)"
        )
        await event.answer("اخبار فرهنگی و هنری")
        await client.send_message(
            message_chat_id, khabar, buttons=news_keyboard, link_preview=False
        )
        await client.edit_message(message_chat_id, event._message_id, buttons=None)

    except Exception as e:
        print("khabar " + str(e))


@client.on(events.CallbackQuery(pattern="Cancel"))
async def callback(event):
    message_chat_id = event.chat_id
    try:
        await client.edit_message(message_chat_id, event._message_id, buttons=keyboard)

    except Exception as e:
        print("khabar " + str(e))


@client.on(events.CallbackQuery(pattern="News"))
async def callback(event):
    message_chat_id = event.chat_id
    global news_id
    news_id = event._message_id
    await client.edit_message(message_chat_id, event._message_id, buttons=news_keyboard)
