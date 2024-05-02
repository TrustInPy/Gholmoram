import re
import json
import aiohttp
import requests
from PIL import Image
from bs4 import BeautifulSoup
from telethon.sync import events, Button
from bot import client, INSTAGRAM_TOKEN, TEMP_CHAT


SIGNATURE = "\n\n----------------------------------------------\n 🔻 @Gholmoram"


async def aiohttp_get(url: str):
    raw_response = None
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Get response status was {response.status}")
            raw_response = await response.content.read()

    return raw_response


@client.on(events.NewMessage(pattern="(?i)/instadl"))
async def callback(event):
    await client.send_message(
        event.chat_id, "توی آپدیت جدید دیگه نیازی به دستور /instadl نیست ✌"
    )


@client.on(events.NewMessage())
async def callback(event):
    user_id = event.sender_id
    url = event.message.raw_text
    if re.match(r"^https?://(www\.)?instagram\.com/.+$", url):
        try:
            status_message = await client.send_message(
                event.chat_id, "در حال جستجو\n-------------------------"
            )
            await download_instagram_media(event.chat_id, url, user_id)
        except Exception as e:
            await client.send_message(
                event.chat_id, f"Error downloading media: {str(e)}"
            )
        finally:
            await client.delete_messages(event.chat_id, status_message)
    else:
        return


async def get_user_id_from_url(url):
    try:
        response = await aiohttp_get(url)
        html_content = response.decode()
        match = re.search(r'"profile_id":"(\d+)"', html_content)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        print(
            "INSTAGRAM - Error in getting user id from instagram view source: \n" + str(e)
        )


async def download_instagram_media(event, url, user_id):
    try:
        username = url.split("/")[4]
        caption_url = "https://www.instagram.com/" + username

        if "instagram.com/p/" in url:
            api_url = f"https://one-api.ir/instagram/?token={INSTAGRAM_TOKEN}&action=post&link={url}"
        
        elif "instagram.com/reel/" in url:
            api_url = f"https://one-api.ir/instagram/?token={INSTAGRAM_TOKEN}&action=audio&link={url}"
       
        elif "instagram.com/stories/" in url:
            user_id = await get_user_id_from_url(caption_url)
            api_url = f"https://one-api.ir/instagram/?token={INSTAGRAM_TOKEN}&action=user_stories&id={user_id}"
            await download_story(event, api_url, user_id, url, caption_url, username)


    except Exception as e:
        print(e)



async def download_story(event, api_url, user_id, url, caption_url, username):
    try:
        response = await aiohttp_get(api_url)
        data = json.loads(response.decode())

        media_files = []
        temp_messages = []

        if not data["result"]:
            await client.send_message(event, "صفحه پرایوت است یا استوری منقضی شده.")
            return


        for media in data["result"]:
            sent_message = await client.send_file(
                TEMP_CHAT, media["url"], caption=user_id, force_document=True
            )

            media_files.append(sent_message.media)
            temp_messages.append(sent_message)

        temp_group = []
        for item in media_files:
            temp_group.append(item)
            if len(temp_group) == 10:
                await client.send_file(event, temp_group, caption=f'[{username}]({caption_url})' + "\n" + SIGNATURE)
                temp_group = []
        if temp_group:
            await client.send_file(event, temp_group, caption=f'[{username}]({caption_url})' + "\n" + SIGNATURE)

    except Exception as e:
        print( "INSTAGRAM - Error in downloading story: " + str(e))
    finally:
        if temp_messages:
            await client.delete_messages(TEMP_CHAT, temp_messages)


# {
#   "status": 200,
#   "result": {
#     "medias": [
#       {
#         "type": "photo",
#         "media": "https://scontent-dfw5-1.cdninstagram.com/v/t51.29350-15/440636623_948497286717581_7314725829324356362_n.jpg?stp=dst-jpg_e35_s1080x1080&efg=eyJ2ZW5jb2RlX3RhZyI6ImltYWdlX3VybGdlbi4xNDQweDE0NDAuc2RyLmYyOTM1MCJ9&_nc_ht=scontent-dfw5-1.cdninstagram.com&_nc_cat=105&_nc_ohc=UtMyRLK3XaoQ7kNvgHQqdO2&edm=ANTKIIoBAAAA&ccb=7-5&oh=00_AfB2qXt9F3lwBvqvey5XpLI5nEnWlYqQCyTdf49n2-6a0w&oe=6636E6EB&_nc_sid=cf751b",
#         "cover": "https://scontent-dfw5-1.cdninstagram.com/v/t51.29350-15/440636623_948497286717581_7314725829324356362_n.jpg?stp=dst-jpg_e35_s1080x1080&_nc_ht=scontent-dfw5-1.cdninstagram.com&_nc_cat=105&_nc_ohc=UtMyRLK3XaoQ7kNvgHQqdO2&edm=ANTKIIoBAAAA&ccb=7-5&oh=00_AfB2qXt9F3lwBvqvey5XpLI5nEnWlYqQCyTdf49n2-6a0w&oe=6636E6EB&_nc_sid=cf751b"
#       },
#       {
#         "type": "photo",
#         "media": "https://scontent-dfw5-1.cdninstagram.com/v/t51.29350-15/440739970_318819211236621_1373273690967404251_n.jpg?stp=dst-jpg_e35_p1080x1080&efg=eyJ2ZW5jb2RlX3RhZyI6ImltYWdlX3VybGdlbi4xMzM1eDEzMzcuc2RyLmYyOTM1MCJ9&_nc_ht=scontent-dfw5-1.cdninstagram.com&_nc_cat=109&_nc_ohc=11nIqKXvBREQ7kNvgGjd6jM&edm=ANTKIIoBAAAA&ccb=7-5&oh=00_AfAG9AUkWQju5euNSn6P_p4qLxmsOnSS0JFmWpSTZnLziA&oe=6636D829&_nc_sid=cf751b",
#         "cover": "https://scontent-dfw5-1.cdninstagram.com/v/t51.29350-15/440739970_318819211236621_1373273690967404251_n.jpg?stp=dst-jpg_e35_p1080x1080&_nc_ht=scontent-dfw5-1.cdninstagram.com&_nc_cat=109&_nc_ohc=11nIqKXvBREQ7kNvgGjd6jM&edm=ANTKIIoBAAAA&ccb=7-5&oh=00_AfAG9AUkWQju5euNSn6P_p4qLxmsOnSS0JFmWpSTZnLziA&oe=6636D829&_nc_sid=cf751b"
#       }
#     ],
#     "caption": "تجسيد محمد ضمن ورشة تعلّم تجسيد الأفكار!🤍\n\nأنا فقط أعدت صياغة التجسيد✨",
#     "owner": {
#       "id": "51178601533",
#       "username": "unsarra",
#       "is_verified": false,
#       "profile_pic_url": "https://scontent-dfw5-2.cdninstagram.com/v/t51.2885-19/431141125_912542427204351_4454950277207538948_n.jpg?stp=dst-jpg_s150x150&_nc_ht=scontent-dfw5-2.cdninstagram.com&_nc_cat=1&_nc_ohc=qOzRJR4y3_UQ7kNvgFSRAAo&edm=ANTKIIoBAAAA&ccb=7-5&oh=00_AfAm3gfowss51aWcTMhQnWnI3DxV80tK6oF_063ubXBTCw&oe=6636E10E&_nc_sid=cf751b",
#       "blocked_by_viewer": false,
#       "restricted_by_viewer": null,
#       "followed_by_viewer": false,
#       "full_name": "سارة غانم",
#       "has_blocked_viewer": false,
#       "is_embeds_disabled": false,
#       "is_private": false,
#       "is_unpublished": false,
#       "requested_by_viewer": false,
#       "pass_tiering_recommendation": true,
#       "edge_owner_to_timeline_media": {
#         "count": 274
#       },
#       "edge_followed_by": {
#         "count": 128700
#       }
#     }
#   }
# }
