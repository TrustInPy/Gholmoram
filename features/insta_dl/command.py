import re
from telethon.sync import events
from bot import client, ADMIN_ID
from instagrapi import Client as cl


@client.on(events.NewMessage(pattern="(?i)/instadl"))
async def callback(event):
    if event.sender_id == ADMIN_ID:
        # Start a new conversation
        async with client.conversation(event.chat_id) as conv:
            # Send a message to the user
            sent_message = await conv.send_message(
                "Please enter the Instagram URL"
            )
            # Get the next message from the user
            response = await conv.get_response()
            if response.sender_id == ADMIN_ID:
                url = response.raw_text
                # Check if the message is in the correct format
                if re.match(r"^https?://(www\.)?instagram\.com/.+$", url):
                    try:
                        download_instagram_media(url, 'user', 'pass')
                        await conv.send_message("Media downloaded successfully")
                    except Exception as e:
                        await conv.send_message(f"Error downloading media: {str(e)}")
                    finally:
                        await client.delete_messages(event.chat_id, sent_message)


def download_instagram_media(url, username, password):
    cli = cl()
    cli.login(username, password)

    media_id = cli.media_pk_from_url(url)
    media = cli.media_info(media_id)

    # media = cli.media_pk_from_url(url)
    # media_info = cli.media_info(media).dict()

    if media.media_type == 2:
        filename = 'media'

        try:
            video_url = cli.media_info(media_id).video_url
            cli.video_download_by_url(video_url, filename)
            print(f"Media downloaded successfully as {filename}")
        except Exception as e:
            print(f"Unable to download media: {str(e)}")

    else:
        print(f"Unable to download images")
        # filename = 'media.jpg'
        # image_url = media['image_versions2']['candidates'][0]['url']
        # response = requests.get(image_url, stream=True)
        # if response.status_code == 200:
        #     with open('media.jpg', 'wb') as out_file:
        #         out_file.write(response.content)
        # else:
        #     print(f"Unable to download image: {response.status_code}")

    # if 'video_versions' in media_info:
    #     # This is a video
    #     video_url = media_info['video_versions'][0]['url']
    #     response = requests.get(video_url, stream=True)
    #     if response.status_code == 200:
    #         with open('media.mp4', 'wb') as out_file:
    #             out_file.write(response.content)
    #     else:
    #         print(f"Unable to download video: {response.status_code}")
    # elif 'image_versions2' in media_info and 'candidates' in media_info['image_versions2']:
    #     # This is an image
    #     image_url = media_info['image_versions2']['candidates'][0]['url']
    #     response = requests.get(image_url, stream=True)
    #     if response.status_code == 200:
    #         with open('media.jpg', 'wb') as out_file:
    #             out_file.write(response.content)
    #     else:
    #         print(f"Unable to download image: {response.status_code}")
    # else:
    #     print("Unable to find video or image versions for the given media ID")
