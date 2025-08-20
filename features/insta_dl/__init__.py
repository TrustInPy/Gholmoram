_FEATURE_NAME = "insta_dl"
_TEMP_DISK_STORAGE_SHARE = 100
_TEMP_MEMORY_STORAGE_SHARE = 100
temp_dir_path: str = f"temp/{_FEATURE_NAME}"
temp_disk_storage = None
temp_memory_storage = None

import logging
from envs import MAX_TEMP_SIZE_DISK, MAX_TEMP_SIZE_MEM
from utilities.simple_temp_storage import DiskStorage, MemoryStorage

_logger = logging.getLogger("main")


if "_active" not in dir():  # Run once
    global _active
    _active = False


def is_active():
    return _active


async def activate():
    global _active
    if is_active():
        return
    await _init()
    _active = True
    _logger.debug(f"features: Feature has been activated: '{_FEATURE_NAME}'")


async def _init():
    # Init temp storages
    if _TEMP_DISK_STORAGE_SHARE > 0:
        global temp_disk_storage
        capacity = MAX_TEMP_SIZE_DISK / 100 * _TEMP_DISK_STORAGE_SHARE
        temp_disk_storage = DiskStorage(name=_FEATURE_NAME, max_capacity=capacity)
        await temp_disk_storage.init()
    if _TEMP_MEMORY_STORAGE_SHARE > 0:
        global temp_memory_storage
        capacity = MAX_TEMP_SIZE_MEM / 100 * _TEMP_MEMORY_STORAGE_SHARE
        temp_disk_storage = MemoryStorage(max_capacity=capacity)


from . import event


async def task_runner():
    if not is_active():
        return
    pass
