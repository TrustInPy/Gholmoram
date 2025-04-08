import aiofiles
import aiohttp
import asyncio
import logging
import re
import os
import uuid
import shutil
import telethon
import aiohttp_socks
from bot import client
from envs import INSTADL_COBALT_API_URL
from features.insta_dl import is_active, temp_dir_path
from features.proxies import proxy_str_list, FEATURE_ALLOW_NO_PROXY
from hachoir.parser import createParser
from yarl import URL

_logger = logging.getLogger("main")

SIGNATURE = "----------------------------------------------\n 🔻 @Gholmoram"


@client.on(telethon.events.NewMessage())
async def handler(event: telethon.events.NewMessage.Event):
    if not is_active():
        return

    chat = event.chat_id
    url = event.message.raw_text
    if not re.match(r"^https?://(www\.)?instagram\.com/.+$", url):
        return
    try:
        status_message = await client.send_message(
            event.chat_id, "در حال جستجو\n-------------------------"
        )
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        data = {"url": url}
        response_json = None
        async with aiohttp.ClientSession() as session:
            async with session.post(
                INSTADL_COBALT_API_URL, headers=headers, json=data
            ) as resp:
                response_json = await resp.json()

        if response_json.get("status") in ["tunnel", "redirect"]:
            media_url = response_json.get("url")
            filename = response_json.get("filename")

            if not media_url or not filename:
                await event.reply("خطا در دیتای بازگشتی درخواست")
                return

            await client.edit_message(
                status_message, "شروع دانلود\n-------------------------"
            )
            files = [{"filename": filename, "url": media_url}]
            downloaded_files, temp_dir = await download_files(files)
            if downloaded_files:
                await client.edit_message(status_message, "در حال ارسال فایل... 🔰")
                await client.send_file(
                    chat,
                    downloaded_files[0],
                    caption=SIGNATURE,
                    reply_to=event.message.id,
                )
        elif response_json.get("status") == "picker":
            files = []
            file_number = 0
            for item in response_json["picker"]:
                filename = str(file_number)
                files.append({"filename": filename, "url": item["url"]})
                file_number += 1
            if response_json.get("audio"):
                filename = str(file_number)
                files.append({"filename": filename, "url": response_json["audio"]})

            downloaded_files, temp_dir = await download_files(files)
            downloaded_files = await _fix_files_extensions(downloaded_files)
            album_files, other_files = separate_files_for_sending_as_album(
                downloaded_files
            )
            if downloaded_files:
                await client.edit_message(status_message, "در حال ارسال... 🔰")
            if album_files:
                await client.send_file(
                    chat,
                    album_files,
                    caption=SIGNATURE,
                    reply_to=event.message.id,
                    album=True,
                    force_document=False,
                )
            if other_files:
                await client.send_file(
                    chat,
                    other_files,
                    reply_to=event.message.id,
                    force_document=True,
                )

        elif response_json.get("status") == "error":
            error = response_json["error"]["code"]
            await event.reply(error)
        else:
            pass
        try:
            await client.delete_messages(chat, status_message)
        except:
            pass

    except Exception as e:
        _logger.error(f"insta_dl: Error processing Instagram link: {str(e)}")
        await event.reply("خطا API")
    finally:
        try:
            await client.delete_messages(event.chat_id, status_message)
        except:
            pass
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


async def download_files(files: list[dict]):
    unique_id = str(uuid.uuid4())
    temp_dir = f"{temp_dir_path()}/{unique_id}"
    os.makedirs(temp_dir)
    result_file_paths = []

    requests = []
    for file in files:
        filepath = f"{temp_dir}/{file["filename"]}"
        requests.append(_download(file["url"], filepath))

    results = await asyncio.gather(*requests)
    for result in results:
        if result["success"]:
            result_file_paths.append(result["filepath"])

    return result_file_paths, temp_dir


async def _download(url: str, filepath: str) -> bool:
    result = {"url": url, "filepath": filepath, "success": False}
    url = URL(url, encoded=True)

    if FEATURE_ALLOW_NO_PROXY:
        success = await _download_without_proxy(url, filepath)
        if success:
            result["success"] = True
            return result

    success = await _download_with_proxy(url, filepath)
    if success:
        result["success"] = True
        return result

    _logger.error(f"insta_dl: Error downloading URL: {url}")
    return result


async def _download_without_proxy(url: str, filepath: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status >= 200 and resp.status < 300:
                    await _save_file(resp, filepath)
                    return True
        return False
    except:
        return False


async def _download_with_proxy(url: str, filepath: str) -> bool:
    for proxy in proxy_str_list:
        try:
            if proxy.startswith("socks5://"):  # socks5 proxy
                connector = aiohttp_socks.ProxyConnector.from_url(proxy)
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.get(url) as resp:
                        if resp.status >= 200 and resp.status < 300:
                            await _save_file(resp, filepath)
                            return True
                        else:
                            raise Exception()
            else:  # http proxy
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, proxy=proxy) as resp:
                        if resp.status >= 200 and resp.status < 300:
                            await _save_file(resp, filepath)
                            return True
                        else:
                            raise Exception()
        except:
            continue  # Try the next proxy
    return False


async def _save_file(resp, filepath):
    async with aiofiles.open(filepath, "wb") as file:
        async for chunk in resp.content.iter_chunked(8192):
            await file.write(chunk)


async def _fix_files_extensions(files: list[str]):
    new_filepaths = []
    for filepath in files:
        ext = _determine_file_extension(filepath)
        if ext:
            new_filepath = f"{filepath}{ext}"
            os.rename(filepath, new_filepath)
            new_filepaths.append(new_filepath)
    return new_filepaths


def _determine_file_extension(filepath: str) -> str | None:
    try:
        with open(filepath, "rb") as file:
            parser = createParser(file)
            if not parser:
                return None
            mime_type = parser.mime_type
    except:
        return None

    mime_to_extension = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/bmp": ".bmp",
        "image/tiff": ".tiff",
        "image/webp": ".webp",
        "text/plain": ".txt",
        "text/html": ".html",
        "text/css": ".css",
        "text/javascript": ".js",
        "application/pdf": ".pdf",
        "application/zip": ".zip",
        "application/x-tar": ".tar",
        "application/x-gzip": ".gz",
        "application/x-rar-compressed": ".rar",
        "application/vnd.ms-excel": ".xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "application/vnd.ms-powerpoint": ".ppt",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
        "application/vnd.word": ".doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/json": ".json",
        "application/xml": ".xml",
        "video/mp4": ".mp4",
        "video/x-msvideo": ".avi",
        "video/x-matroska": ".mkv",
        "video/quicktime": ".mov",
        "video/x-flv": ".flv",
        "video/x-ms-wmv": ".wmv",
        "audio/mpeg": ".mp3",
        "audio/wav": ".wav",
        "audio/ogg": ".ogg",
        "audio/x-flac": ".flac",
        "audio/x-ms-wma": ".wma",
        "audio/aac": ".aac",
        "application/octet-stream": ".bin",
    }

    return mime_to_extension.get(mime_type)


def separate_files_for_sending_as_album(files: list[str]):
    files_as_album = []
    other_files = []
    for file in files:
        ext = file.split(".")[-1]
        if not ext:
            continue
        if ext in ["jpg", "png", "bmp", "mp4"]:
            files_as_album.append(file)
        else:
            other_files.append(file)

    return files_as_album, other_files
