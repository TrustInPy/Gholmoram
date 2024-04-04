import re
import os
import aiosqlite
from PIL import Image
from instagrapi import Client as cl
from telethon.sync import events, Button
from bot import client, DATABASE_NAME, INSTA_USERNAME, INSTA_PASSWORD, HOME_ID


SIGNATURE = "\n\n----------------------------------------------\n 🔻 @Gholmoram"


async def insta_login():
    global cli
    cli = cl()
    try:
        cli.load_settings("InstaSession.json")
        cli.login(INSTA_USERNAME, INSTA_PASSWORD)
        cli.get_timeline_feed()
    except Exception as e:
        print(e)
        cli = cl()
        cli.login(INSTA_USERNAME, INSTA_PASSWORD)
        cli.dump_settings("InstaSession.json")


@client.on(events.NewMessage(pattern="(?i)/instadl"))
async def callback(event):
    await client.send_message(
        event.chat_id, "توی آپدیت جدید دیگه نیازی به دستور /instadl نیست ✌"
    )


@client.on(events.NewMessage())
async def callback(event):
    # connection = await aiosqlite.connect(DATABASE_NAME)
    # cursor = await connection.cursor()
    # await cursor.execute("SELECT user_id FROM admins")
    # result = await cursor.fetchall()
    # await connection.close()
    # admins = [row[0] for row in result]
    # if event.sender_id in admins:
    downloader_use = event.sender_id
    url = event.message.raw_text
    if re.match(r"^https?://(www\.)?instagram\.com/.+$", url):
        try:
            status_message = await client.send_message(
                event.chat_id, "در حال جستجو\n-------------------------"
            )
            await download_instagram_media(event, url, status_message)
        except Exception as e:
            await client.send_message(
                event.chat_id, f"Error downloading media: {str(e)}"
            )
        finally:
            await client.delete_messages(event.chat_id, status_message)
    else:
        return


async def download_instagram_media(event, url, status_message):
    try:
        media_id = None
        if "stories" in url:
            parts = url.split("?")
            path = parts[0]
            path_parts = [part for part in path.split("/") if part]
            media_id = path_parts[-1]
        elif "instagram.com/" in url:
            match = re.search(r"instagram\.com/(.+)/(.+)/", url)
            if match:
                media_code_or_id = match.group(2).split("?")[0]
                if re.match(r"^[A-Za-z0-9_-]+$", media_code_or_id):
                    media_id = cli.media_pk_from_code(media_code_or_id)
                else:
                    media_id = media_code_or_id
        if not media_id:
            raise ValueError("Could not extract media ID from URL")
        media = cli.media_info(media_id)
        await client.edit_message(
            status_message, "شروع دانلود\n-------------------------"
        )

        if media.media_type == 1:
            # Photo
            path = cli.photo_download(media.pk)
            if path.suffix == ".heic":
                await client.edit_message(
                    status_message, "در حال ارسال\n-------------------------"
                )
                im = Image.open(path)
                jpeg_path = path._str.rsplit(".", 1)[0] + ".jpeg"
                im.save(jpeg_path, "JPEG")
                pathjpeg = jpeg_path
                if media.caption_text:
                    caption = (
                        f"[@{media.user.username}](instagram.com/{media.user.username})"
                        + "\n\n"
                        + media.caption_text[:800]
                        + SIGNATURE
                    )
                else:
                    caption = (
                        f"[@{media.user.username}](instagram.com/{media.user.username})"
                        + "\n\n"
                        + SIGNATURE
                    )
                await client.send_file(event.chat_id, pathjpeg, caption=caption)
                try:
                    os.remove(path)
                    os.remove(pathjpeg)
                except:
                    pass
            elif path.suffix == ".webp":
                await client.edit_message(
                    status_message, "در حال ارسال\n-------------------------"
                )
                im = Image.open(path)
                jpeg_path = path._str.rsplit(".", 1)[0] + ".jpeg"
                im.save(jpeg_path, "JPEG")
                pathjpeg = jpeg_path
                if media.caption_text:
                    caption = (
                        f"[@{media.user.username}](instagram.com/{media.user.username})"
                        + "\n\n"
                        + media.caption_text[:800]
                        + SIGNATURE
                    )
                else:
                    caption = (
                        f"[@{media.user.username}](instagram.com/{media.user.username})"
                        + "\n\n"
                        + SIGNATURE
                    )
                await client.send_file(event.chat_id, pathjpeg, caption=caption)
                try:
                    os.remove(path)
                    os.remove(pathjpeg)
                except:
                    pass
            else:
                await client.edit_message(
                    status_message, "در حال ارسال\n-------------------------"
                )
                if media.caption_text:
                    caption = (
                        f"[@{media.user.username}](instagram.com/{media.user.username})"
                        + "\n\n"
                        + media.caption_text[:800]
                        + SIGNATURE
                    )
                else:
                    caption = (
                        f"[@{media.user.username}](instagram.com/{media.user.username})"
                        + "\n\n"
                        + SIGNATURE
                    )
                await client.send_file(event.chat_id, path, caption=caption)
                os.remove(path)

        elif media.media_type == 2:
            path = cli.video_download(media.pk)
            await client.edit_message(
                status_message, "در حال ارسال\n-------------------------"
            )
            if media.caption_text:
                caption = (
                    f"[@{media.user.username}](instagram.com/{media.user.username})"
                    + "\n\n"
                    + media.caption_text[:800]
                    + SIGNATURE
                )
            else:
                caption = (
                    f"[@{media.user.username}](instagram.com/{media.user.username})"
                    + "\n\n"
                    + SIGNATURE
                )
            await client.send_file(event.chat_id, path, caption=caption)
            os.remove(path)

        elif media.media_type == 8:
            # Album
            files = []
            for path in cli.album_download(media.pk):
                if path.suffix == ".heic":
                    im = Image.open(path)
                    jpeg_path = path._str.rsplit(".", 1)[0] + ".jpeg"
                    im.save(jpeg_path, "JPEG")
                    pathjpeg = jpeg_path
                    files.append(pathjpeg)
                    try:
                        os.remove(path)
                    except:
                        pass
                elif path.suffix == ".webp":
                    im = Image.open(path)
                    jpeg_path = path._str.rsplit(".", 1)[0] + ".jpeg"
                    im.save(jpeg_path, "JPEG")
                    pathjpeg = jpeg_path
                    files.append(pathjpeg)
                    try:
                        os.remove(path)
                    except:
                        pass
                else:
                    files.append(path._str)
            await client.edit_message(
                status_message, "در حال ارسال\n-------------------------"
            )
            if media.caption_text:
                caption = (
                    f"[@{media.user.username}](instagram.com/{media.user.username})"
                    + "\n\n"
                    + media.caption_text[:800]
                    + SIGNATURE
                )
            else:
                caption = (
                    f"[@{media.user.username}](instagram.com/{media.user.username})"
                    + "\n\n"
                    + SIGNATURE
                )
            await client.send_file(event.chat_id, files, caption=caption)
            for file in files:
                try:
                    os.remove(file)
                except:
                    pass
    except Exception as e:
        mention = f"[User {event.sender_id}](tg://user?id={event.sender_id})"
        selection = (
            "👤 "
            + mention
            + "\n\n"
            + "Faield to download: \n"
            + url
            + "\n"
            + "with instadl.\n\n"
            + "#log"
        )
        await client.send_message(HOME_ID, selection)

        await client.send_message(
            event.chat_id,
            "صفحه مورد نظر Private است یا لینک نامعتبر است.",
        )
        print(f"An error occurred instadl: {str(e)}")
