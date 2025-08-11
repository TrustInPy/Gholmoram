import aiofiles
import aiohttp
import asyncio
import io
import os
import shutil
import time
import uuid
from . import FileTooLargeError, NotEnoughSpaceError, UnsupportedInputError
from utilities import hachoir_mime
from utilities.simple_sqlite_interface import SqliteInterface


class DiskStorage:
    """
    Simple on-disk temp storage.
    Automatically trims storage according to the `max_capacity`.
    """

    def __init__(
        self,
        name: str,
        max_capacity: int,
        max_allowed_file_size: int = None,
        min_persist_time: int = 600,
        headroom_percent: int = 10,
        persist_storage: bool = True,
        cache_data: bool = True,
        temp_path: str = "./temp",
        data_path: str = "./data/utilities",
    ):
        """
        Args:
            `name`: A unique name for this storage.
            `max_capacity`: Max storage capacity in bytes.
            `max_allowed_file_size`: Largest acceptable file size. None means no limit.
            `min_persist_time`: Minimum span of time which the objects are kept
                before getting trimmed.
            `headroom_percent`: Percentage of storage size to trim in advance.
            `persist_data`: Do not clear the temp storage after restart.
            `cache_data`: Store new data changes to memory for faster operations.
                Cache gets written to DB at time intervals.
            `temp_path`: Directory path to store temp files.
            `data_path`: Directory path to store database file.
        """
        self.__name: str = name
        self.__max_capacity: int = max_capacity
        self.__max_allowed_file_size: int | None = max_allowed_file_size
        self.__min_persist_time: int = min_persist_time
        self.__headroom_percent: int = headroom_percent
        self.__persist_storage: bool = persist_storage
        self.__cache_data: bool = cache_data
        self.__temp_path: str = temp_path
        self.__data_path: str = data_path

        self.__data_lock = asyncio.Lock()
        self.__current_size: int = 0
        self.__pending_files: dict = {}
        self.__pending_files_lock = asyncio.Lock()

        self.__interval_cache_write: int = 5
        self.__last_cache_write: int = int(time.time())
        self.__last_tasks_trigger: int = int(time.time())
        self.__interval_backup_tasks_trigger: int = 30

        self.__memory_data_files_stored = {}
        self.__memory_data_files_donewith = {}
        self.__memory_data_files_retrieved = {}
        self.__memory_data_lock = asyncio.Lock()

    async def init(self):
        os.makedirs(self.__root(), exist_ok=True)
        async with self.__data_lock:
            await self.__init_db()

        if not self.__persist_storage:
            await self.purge()
            await self.close()
            try:
                os.remove(
                    f"{self.__data_path}/simple_temp_storage/{self.__name}/data.db"
                )
            except:
                pass
            async with self.__data_lock:
                await self.__init_db()

        await self.delete_headless_files()

    async def __init_db(self):
        os.makedirs(
            f"{self.__data_path}/simple_temp_storage/{self.__name}", exist_ok=True
        )
        self.__db = SqliteInterface(
            f"{self.__data_path}/simple_temp_storage/{self.__name}/data.db"
        )
        await self.__db.init()
        # Table structure
        query = """
            CREATE TABLE IF NOT EXISTS "files" (
                "key"               TEXT PRIMARY KEY,
                "extension"         TEXT NULL,
                "size"              INTEGER NOT NULL,
                "last_used"         INTEGER NOT NULL,
                "done_with"         INTEGER NOT NULL DEFAULT 0
            );
        """
        await self.__db.execute(query, commit=True)

        # Index on last_used
        query = """
            CREATE INDEX IF NOT EXISTS idx_files_last_used on "files" ("last_used" ASC);
        """
        await self.__db.execute(query, commit=True)

        await self.__load_metadata()

    async def close(self):
        """Write any data in cache to the database and close the
        underlying sqlite connection.
        """
        async with self.__memory_data_lock:
            await self.__write_all_cache_now()
        await self.__db.close()

    async def __load_metadata(self):
        # Load previous stored metadata
        query = """
            SELECT SUM(size) FROM files
        """
        result = await self.__db.execute(query, fetchone=True)
        if not result[0] is None:
            self.__current_size = result[0]

    def __root(self) -> str:
        return f"{self.__temp_path}/simple_temp_storage/{self.__name}"

    def __file_dir(self, key) -> str:
        return f"{self.__root()}/{key[0:2]}"

    def __file_path(self, key) -> str:
        return f"{self.__file_dir(key)}/{key}"

    async def store(self, input) -> str:
        """
        Args:
            `input`: aiohttp.StreamReader, io.BytesIO, bytes or bytearray
        Returns:
            str: Stored object's access key
        """
        await self.__trigger_tasks_backup()
        key = str(uuid.uuid4())
        file_path = self.__file_path(key)
        async with self.__pending_files_lock:
            self.__pending_files[key] = True

        try:
            os.makedirs(self.__file_dir(key), exist_ok=True)
            # store on disk without extension
            if isinstance(input, aiohttp.StreamReader):
                async with aiofiles.open(file_path, "wb") as f:
                    while True:
                        chunk = await input.read(8192)
                        if not chunk:
                            break
                        await f.write(chunk)
            elif isinstance(input, io.BytesIO):
                async with aiofiles.open(file_path, "wb") as f:
                    input.seek(0)
                    await f.write(input.read())
            elif isinstance(input, bytes):
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(input)
            elif isinstance(input, bytearray):
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(input)
            else:
                raise UnsupportedInputError()

            # Check file size
            file_size = os.path.getsize(file_path)
            if self.__max_allowed_file_size:
                if file_size > self.__max_allowed_file_size:
                    raise FileTooLargeError(str(file_size))

            # Trim storage if needed before accepting new item
            async with self.__data_lock:
                await self.__trim(file_size)
                self.__current_size += file_size

            file_ext = await hachoir_mime.determine_file_extension(file_path)
            if file_ext:
                os.rename(file_path, f"{file_path}{file_ext}")
            await self.__store(key, file_ext, file_size)
            return key
        except:
            try:
                os.remove(file_path)
            except:
                pass
            raise
        finally:
            try:
                async with self.__pending_files_lock:
                    del self.__pending_files[key]
            except:
                pass

    async def donewith(self, key) -> None:
        """
        Call this method when you are done with the temp file.
        """
        await self.__trigger_tasks_backup()
        await self.__donewith(key)

    async def retrieve(self, key) -> str | None:
        """
        Retrieve temp file path by providing the key.
        """
        await self.__trigger_tasks_backup()
        return await self.__retrieve(key)

    async def purge(self) -> None:
        """
        Delete all data and stored files.
        """
        async with self.__data_lock:
            try:
                shutil.rmtree(self.__root())
            except:
                pass
            query = """
                DELETE FROM files
            """
            await self.__db.execute(query, commit=True)
            self.__current_size = 0

    async def consumed_size(self):
        """
        Get storage consumed size in bytes.
        """
        await self.__trigger_tasks_backup()
        async with self.__data_lock:
            return self.__current_size

    async def delete_headless_files(self):
        """
        Remove files are not being tracked (dangling files).
        Caution: This method also deletes all files and directories which
        are out of predefined structure.
        """
        if not os.path.exists(self.__root()):
            return

        for item in os.listdir(self.__root()):
            item_path = os.path.join(self.__root(), item)
            if not os.path.isdir(item_path):
                # file
                try:
                    os.remove(item_path)
                except:
                    pass
                continue

            # directory
            for item2 in os.listdir(item_path):
                item2_path = os.path.join(item_path, item2)
                if os.path.isdir(item2_path):
                    # directory
                    try:
                        shutil.rmtree(item2_path)
                    except:
                        pass
                else:
                    # file
                    key = item2.split(".")[0]
                    async with self.__pending_files_lock:
                        if self.__pending_files.get(key):
                            continue

                    query = """
                        SELECT COUNT(*) FROM files
                        WHERE key = ?
                    """
                    count = await self.__db.execute(query, (key,), fetchone=True)
                    if count[0] == 0:
                        try:
                            os.remove(item2_path)
                        except:
                            pass

    async def trigger_tasks(self):
        """
        Try to run scheduled tasks. Run this method at a constant interval e.g. every second.
        """
        if not self.__cache_data:
            return

        now = int(time.time())
        if now - self.__last_cache_write >= self.__interval_cache_write:
            async with self.__memory_data_lock:
                await self.__write_all_cache_now()

        self.__last_tasks_trigger = now

    async def __trigger_tasks_backup(self):
        """
        Backup trigger for running tasks if the main trigger is not called.
        """
        if not self.__cache_data:
            return

        now = int(time.time())
        if now - self.__last_tasks_trigger >= self.__interval_backup_tasks_trigger:
            async with self.__memory_data_lock:
                await self.__write_all_cache_now()

        self.__last_tasks_trigger = now

    async def __write_all_cache_now(self):
        await self.__write_cache_insert()
        await self.__write_cache_retrieve()
        await self.__write_cache_donewith()
        self.__last_cache_write = int(time.time())

    async def __write_cache_insert(self):
        try:
            query = """
                INSERT INTO files (key, extension, size, last_used, done_with)
                VALUES (?, ?, ?, ?, ?)
            """
            params_list: list[tuple] = []
            for key in self.__memory_data_files_stored.keys():
                params_list.append(
                    (
                        key,
                        self.__memory_data_files_stored[key]["extension"],
                        self.__memory_data_files_stored[key]["size"],
                        self.__memory_data_files_stored[key]["last_used"],
                        self.__memory_data_files_stored[key]["done_with"],
                    )
                )
                if len(params_list) == 20000:
                    await self.__db.executemany(query, params_list, commit=True)
                    params_list = []

            if len(params_list) > 0:
                await self.__db.executemany(query, params_list, commit=True)
        finally:
            self.__memory_data_files_stored = {}

    async def __write_cache_donewith(self):
        try:
            query = """
                UPDATE files
                SET done_with = ?
                WHERE key = ?
            """
            params_list: list[tuple] = []
            for key in self.__memory_data_files_donewith.keys():
                params_list.append((1, key))
                if len(params_list) == 20000:
                    await self.__db.executemany(query, params_list, commit=True)
                    params_list = []

            if len(params_list) > 0:
                await self.__db.executemany(query, params_list, commit=True)
        finally:
            self.__memory_data_files_donewith = {}

    async def __write_cache_retrieve(self):
        try:
            query = """
                UPDATE files
                SET last_used = ?,
                    done_with = 0
                WHERE key = ?
            """
            params_list: list[tuple] = []
            for key in self.__memory_data_files_retrieved.keys():
                params_list.append((self.__memory_data_files_retrieved[key], key))
                if len(params_list) == 20000:
                    await self.__db.executemany(query, params_list, commit=True)
                    params_list = []

            if len(params_list) > 0:
                await self.__db.executemany(query, params_list, commit=True)
        finally:
            self.__memory_data_files_retrieved = {}

    async def __trim(self, needed_size: int = 0):
        """Make room if needed."""
        if self.__current_size + needed_size <= self.__max_capacity:
            # There is already enough space
            return

        if needed_size > self.__max_capacity:
            raise NotEnoughSpaceError("This file cannot fit in this temp storage")

        headroom = self.__max_capacity / 100 * self.__headroom_percent
        try_to_free = self.__current_size - self.__max_capacity + headroom
        min_space_to_free = self.__current_size - self.__max_capacity + needed_size
        freed = 0
        enough = False
        min_allowed_last_used_time = int(time.time()) - self.__min_persist_time

        # Query expired entries with flag "done_with" set to True (in batches)
        select_query = f"""
            SELECT key, extension, size FROM files
            WHERE done_with = 1 AND last_used < {min_allowed_last_used_time}
            ORDER BY last_used ASC
            LIMIT ?
        """
        enough, freed_here = await self.__query_and_trim(select_query, try_to_free)
        freed += freed_here
        try_to_free -= freed_here

        if enough:
            return

        # Query expired entries (in batches)
        select_query = f"""
            SELECT key, extension, size FROM files
            WHERE last_used < {min_allowed_last_used_time}
            ORDER BY last_used ASC
            LIMIT ?
        """
        enough, freed_here = await self.__query_and_trim(select_query, try_to_free)
        freed += freed_here
        try_to_free -= freed_here

        if enough:
            return

        # Query all entries with flag "done_with" set to True (in batches)
        select_query = f"""
            SELECT key, extension, size FROM files
            WHERE done_with = 1
            ORDER BY last_used ASC
            LIMIT ?
        """
        enough, freed_here = await self.__query_and_trim(select_query, try_to_free)
        freed += freed_here
        try_to_free -= freed_here

        if enough:
            return

        if freed >= min_space_to_free:
            return

        raise NotEnoughSpaceError(f"needed {needed_size} bytes")

    async def __query_and_trim(self, select_query, try_to_free):
        delete_query = """
            DELETE FROM files
            WHERE key = ?
        """
        freed = 0
        enough = False
        while True:
            keys_to_delete = []
            batch_size = 5000
            rows = await self.__db.execute(
                select_query, params=(batch_size,), fetchall=True
            )
            for row in rows:
                async with self.__memory_data_lock:
                    if self.__memory_data_files_retrieved.get(row[0]):
                        continue
                keys_to_delete.append((row[0],))
                file_path = self.__file_path(row[0])
                if row[1]:  # file extension
                    file_path = f"{file_path}{row[1]}"
                try:
                    os.remove(file_path)
                except:
                    pass
                self.__current_size -= row[2]
                freed += row[2]

                if freed >= try_to_free:
                    enough = True
                    break

            if len(keys_to_delete) > 0:
                await self.__db.executemany(delete_query, keys_to_delete, commit=True)

            if enough or len(rows) < batch_size:
                break

        return enough, freed

    async def __store(self, key, extension, size):
        if self.__cache_data:
            async with self.__memory_data_lock:
                self.__memory_data_files_stored[key] = {
                    "extension": extension,
                    "size": size,
                    "last_used": int(time.time()),
                    "done_with": False,
                }
        else:
            query = """
                INSERT INTO files (key, extension, size, last_used)
                VALUES (?, ?, ?, ?)
            """
            await self.__db.execute(
                query, (key, extension, size, int(time.time())), commit=True
            )

    async def __donewith(self, key):
        if self.__cache_data:
            async with self.__memory_data_lock:
                stored_file = self.__memory_data_files_stored.get(key)
                if stored_file:
                    stored_file["done_with"] = True
                else:
                    self.__memory_data_files_donewith[key] = True
        else:
            query = """
                UPDATE files
                SET done_with = ?
                WHERE key = ?
            """
            await self.__db.execute(query, (1, key), commit=True)

    async def __retrieve(self, key):
        key_found = False
        file_ext = None

        if self.__cache_data:
            async with self.__memory_data_lock:
                stored_file = self.__memory_data_files_stored.get(key)
                if stored_file:
                    stored_file["last_used"] = int(time.time())
                    stored_file["done_with"] = False
                    key_found = True
                    file_ext = stored_file["extension"]
                else:
                    self.__memory_data_files_retrieved[key] = int(time.time())
                    try:
                        del self.__memory_data_files_donewith[key]
                    except:
                        pass
                    if len(self.__memory_data_files_retrieved.keys()) >= 500:
                        await self.__write_all_cache_now()
                    query = """
                        SELECT key, extension FROM files
                        WHERE key = ?
                    """
                    row = await self.__db.execute(query, (key,), fetchone=True)
                    if row:
                        key_found = True
                        file_ext = row[1]
        else:
            query = """
                SELECT key, extension FROM files
                WHERE key = ?
            """
            row = await self.__db.execute(query, (key,), fetchone=True)
            if row:
                key_found = True
                file_ext = row[1]

            query = """
                UPDATE files
                SET last_used = ?,
                    done_with = 0
                WHERE key = ?
            """
            await self.__db.execute(query, (int(time.time()), key), commit=True)

        if not key_found:
            return None

        file_path = self.__file_path(key)
        if file_ext:
            file_path = f"{file_path}{file_ext}"

        return file_path
