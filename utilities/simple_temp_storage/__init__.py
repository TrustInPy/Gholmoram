class FileTooLargeError(Exception):
    def __init__(self, value, message="File size exceeds max allowed size"):
        self.value = value
        self.message = message
        super().__init__(f"{self.message}: {self.value}")


class NotEnoughSpaceError(Exception):
    def __init__(self, value, message="There is not enough space in the storage"):
        self.value = value
        self.message = message
        super().__init__(f"{self.message}: {self.value}")


class UnsupportedInputError(Exception):
    def __init__(self, value, message="Unsupported input"):
        self.value = value
        self.message = message
        super().__init__(f"{self.message}: {self.value}")


from .disk_storage import DiskStorage
from .memory_storage import MemoryStorage
