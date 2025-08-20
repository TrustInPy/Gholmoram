import aiofiles
import aiohttp
import io
import os
import uuid
from . import StoreResult, StoreResultStatus
from utilities import hachoir_mime


class UnManagedDiskStorage:
    """Store temp files in the given directory."""

    def __init__(self, directory: str, max_allowed_file_size: int = None):
        """
        Args:
            `directory`: The destination directory.
            `max_allowed_file_size`: Largest acceptable file size. None means no limit.
        """
        self.__directory = directory
        self.max_allowed_file_size = max_allowed_file_size

    async def store(self, input, force_keep: bool = False) -> StoreResult:
        """
        Args:
            `input`: aiohttp.StreamReader, io.BytesIO, bytes or bytearray
            `force_keep`: Keep the file on the disk whether it's healthy or incomplete.
                Using this option makes the storage manager to not track the file so
                deletion of the file should be handled externally.
        Returns:
            StoreResult: The result object of the store operation
        """
        store_successful = False
        store_result = StoreResult()
        key = str(uuid.uuid4())
        file_path = f"{self.__directory}/{key}"

        try:
            os.makedirs(self.__directory, exist_ok=True)
            # store on disk without extension
            if isinstance(input, aiohttp.StreamReader):
                async with aiofiles.open(file_path, "wb") as f:
                    written_size = 0
                    while True:
                        chunk = await input.read(8192)
                        if not chunk:
                            break
                        await f.write(chunk)
                        written_size += len(chunk)
                        if written_size > self.max_allowed_file_size:
                            if force_keep:
                                store_result.file_path = file_path
                            store_result.status = (
                                StoreResultStatus.EXCEEDED_MAX_ALLOWED_SIZE
                            )
                            return store_result

            elif isinstance(input, io.BytesIO):
                async with aiofiles.open(file_path, "wb") as f:
                    written_size = 0
                    input.seek(0)
                    while True:
                        chunk = input.read(8192)
                        if not chunk:
                            break
                        await f.write(chunk)
                        written_size += len(chunk)
                        if written_size > self.max_allowed_file_size:
                            if force_keep:
                                store_result.file_path = file_path
                            store_result.status = (
                                StoreResultStatus.EXCEEDED_MAX_ALLOWED_SIZE
                            )
                            return store_result

            elif isinstance(input, bytes):
                if len(input) > self.max_allowed_file_size:
                    store_result.status = StoreResultStatus.EXCEEDED_MAX_ALLOWED_SIZE
                    return store_result
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(input)

            elif isinstance(input, bytearray):
                if len(input) > self.max_allowed_file_size:
                    store_result.status = StoreResultStatus.EXCEEDED_MAX_ALLOWED_SIZE
                    return store_result
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(input)

            else:
                store_result.status = StoreResultStatus.UNSUPPORTED_INPUT
                return store_result

            file_ext = await hachoir_mime.determine_file_extension(file_path)
            if file_ext:
                new_file_path = f"{file_path}{file_ext}"
                os.rename(file_path, new_file_path)
                file_path = new_file_path

            store_result.key = key
            store_result.file_path = file_path
            store_successful = True
            return store_result
        finally:
            if not store_successful and not force_keep:
                try:
                    os.remove(file_path)
                except:
                    pass
