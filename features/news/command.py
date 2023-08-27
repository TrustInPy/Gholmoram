import requests
from bot import client
from telethon.sync import events


@client.on(
    events.NewMessage(func=lambda e: e.is_group or e.is_private, pattern="(?i)/news")
)
async def news(event):
    message_chat_id = event.chat_id
    max_length = 30
    try:
        url = "https://www.farsnews.ir/rss/topnews"
        response = requests.get(url)
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
            # pub_date = item_tag.split("<pubDate>")[1].split("</pubDate>")[0]
            khabar = khabar + f"🔅 [{title}]({link})\n "
        khabar = (
            "📌 ‏**اخبار برتر روز:**\n"
            + khabar
            + "\n🌐 [Farsnews](https://www.farsnews.ir)"
        )
        await client.send_message(message_chat_id, khabar, link_preview=False)

    except Exception as e:
        print("khabar" + str(e))
