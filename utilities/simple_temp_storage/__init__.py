from enum import Enum


class StoreResultStatus(Enum):
    SUCCESS = 0
    UNSUPPORTED_INPUT = 1
    NOT_ENOUGH_SPACE = 2
    EXCEEDED_MAX_ALLOWED_SIZE = 3


class StoreResult:
    def __init__(
        self, status: StoreResultStatus, key: str = None, file_path: str = None
    ):
        self.status = status
        self.key = key
        self.file_path = file_path


from .disk_storage import DiskStorage
from .memory_storage import MemoryStorage
from .unmanaged_disk_storage import UnManagedDiskStorage
