import aiofiles
import aiohttp
import aiohttp_socks
import asyncio
import io
import os
from enum import Enum
from utilities.simple_temp_storage import (
    DiskStorage,
    MemoryStorage,
    UnManagedDiskStorage,
    StoreResult,
    StoreResultStatus,
)
from yarl import URL


class Expect(Enum):
    NONE = 0
    TEXT = 1
    JSON = 2
    BYTES = 3


# Default settings
_TRY_NO_PROXY = True
_PROXIES = []
_RETRIES = 0
_TIMEOUT = 3


def set_proxies(proxies: list, allow_no_proxy: bool = True):
    global _PROXIES, _TRY_NO_PROXY
    _PROXIES = proxies
    _TRY_NO_PROXY = allow_no_proxy


async def get(
    url: str,
    expect: Expect = Expect.NONE,
    retries: int = None,
    timeout: int = None,
) -> dict:
    if not retries:
        retries = _RETRIES
    if not timeout:
        retries = _TIMEOUT
    pass


async def post(
    url: str,
    body: str,
    expect: Expect = Expect.NONE,
    retries: int = None,
    timeout: int = None,
) -> dict:
    if not retries:
        retries = _RETRIES
    if not timeout:
        retries = _TIMEOUT
    pass


async def download_urls_as_files(
    urls: list[str], storages: list, retries: int = None, timeout: int = None
) -> list[dict]:
    """
    Download multiple URLs as files and store them in the desired place.
    Args:
        `urls`: list of URLs
        `storages`: List of preferred storages to store downloaded files to.
        `retries`: Number of retries if download failed.
        `timeout`: Web request timeout.
    At least one storage must be specified.
    If more than one storage is provided the one with lower index has higher priority.
    """
    results: list[dict] = []
    download_jobs = []
    for url in urls:
        download_jobs.append(download_url_as_file(url, storages, retries, timeout))
    results = await asyncio.gather(*download_jobs)
    return results


async def download_url_as_file(
    url: str, storages: list, retries: int = None, timeout: int = None
) -> dict:
    """
    Download URL as file and store it in the desired place.
    Args:
        `url`: the URL
        `storages`: List of preferred storages to store downloaded files to.
        `retries`: Number of retries if download failed.
        `timeout`: Web request timeout.
    At least one storage must be specified.
    If more than one storage is provided the one with lower index has higher priority.
    """
    if not storages or len(storages) == 0:
        raise Exception("At least one storage should be provided.")

    result = {"url": url, "success": False, "file": None}
    url = URL(url, encoded=True)

    retries = retries if retries is not None else _RETRIES
    timeout = timeout if timeout is not None else _TIMEOUT

    for _ in range(retries + 1):
        if _TRY_NO_PROXY:
            try:
                stored_file = await _download_without_proxy(
                    url, storages, retries, timeout
                )
                result["file"] = stored_file
                result["success"] = True
                break
            except:
                pass

        try:
            stored_file = await _download_with_proxy(url, storages, retries, timeout)
            result["file"] = stored_file
            result["success"] = True
            break
        except:
            pass

    return result


async def _download_without_proxy(url: str, storages: list, timeout: int) -> dict:
    timeout_object = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(timeout=timeout_object) as session:
        async with session.get(url) as resp:
            if resp.status >= 200 and resp.status < 300:
                return await __save_file(resp.content, storages)


async def _download_with_proxy(url: str, storages: list, timeout: int) -> dict:
    for proxy in _PROXIES:
        try:
            timeout_object = aiohttp.ClientTimeout(total=timeout)
            if proxy.startswith("socks5://"):  # socks5 proxy
                connector = aiohttp_socks.ProxyConnector.from_url(proxy)
                async with aiohttp.ClientSession(
                    connector=connector, timeout=timeout_object
                ) as session:
                    async with session.get(url) as resp:
                        if resp.status >= 200 and resp.status < 300:
                            return __save_file(resp.content, storages)
            else:  # http proxy
                async with aiohttp.ClientSession(timeout=timeout_object) as session:
                    async with session.get(url, proxy=proxy) as resp:
                        if resp.status >= 200 and resp.status < 300:
                            return await __save_file(resp.content, storages)
        except:
            continue  # Try the next proxy

    raise Exception()


async def __save_file(resp: aiohttp.ClientResponse, storages: list) -> dict:
    try:
        buffer = bytearray()
        incomplete_file_path = None
        for storage in storages:
            if isinstance(storage, MemoryStorage):
                if incomplete_file_path:
                    file_size = os.path.getsize(incomplete_file_path)
                    if file_size > storage.max_allowed_file_size:
                        continue
                    buffer = bytearray()
                    async with aiofiles.open(incomplete_file_path, "rb") as file:
                        while True:
                            chunk = await file.read(8192)
                            if not chunk:
                                break
                            buffer.extend(chunk)
                    try:
                        os.remove(incomplete_file_path)
                    except:
                        pass
                while True:
                    chunk = await resp.content.read(8192)
                    if not chunk:
                        break
                    buffer.extend(chunk)
                    if len(buffer) > storage.max_allowed_file_size:
                        break
                if len(buffer) > storage.max_allowed_file_size:
                    continue
                store_result = await storage.store(buffer)
                if store_result.status == StoreResultStatus.SUCCESS:
                    return {"storage_type": "memory", "key": store_result.key}

            elif isinstance(storage, DiskStorage) or isinstance(
                storage, UnManagedDiskStorage
            ):
                if incomplete_file_path:
                    input1 = incomplete_file_path
                    current_size = os.path.getsize(input1) 
                else:
                    input1 = buffer
                    current_size = len(input1)
                if current_size > storage.max_allowed_file_size:
                    continue
                store_result = await storage.store(
                    combine_streams(input1, resp.content), force_keep=True
                )
                if store_result.status == StoreResultStatus.SUCCESS:
                    return {
                        "storage_type": "disk",
                        "key": store_result.key,
                        "path": store_result.file_path,
                    }
                else:
                    new_size = os.path.getsize(store_result.file_path)
                    if new_size > current_size:
                        try:
                            del buffer
                            os.remove(incomplete_file_path)
                        except:
                            pass
                        incomplete_file_path = store_result.file_path
                    else:
                        try:
                            os.remove(store_result.file_path)
                        except:
                            pass

            else:
                raise Exception("Unknown provided storage.")

        raise Exception(
            "Saving web response was not successful after trying all provided storages."
        )
    finally:
        try:
            del buffer
        except:
            pass
        try:
            os.remove(incomplete_file_path)
        except:
            pass


# UNTESTED
async def combine_streams(input1, input2):
    # Create an asynchronous generator to yield data from both streams
    async def combined_stream():
        # Serve input1
        if isinstance(input1, bytearray):
            stream1 = io.BytesIO(input1)
            while True:
                chunk = stream1.read(8192)
                if not chunk:
                    break
                yield chunk
        elif isinstance(input1, str):
            async with aiofiles.open(input2, "rb") as stream1:
                while True:
                    chunk = await stream1.read(8192)
                    if not chunk:
                        break
                    yield chunk

        # Serve input2
        if isinstance(input2, aiohttp.StreamReader):
            while True:
                chunk = await input2.read(8192)
                if not chunk:
                    break
                yield chunk

    return combined_stream
