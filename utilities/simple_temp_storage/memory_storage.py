import asyncio
import heapq
import sys
import time
import uuid
from . import NotEnoughSpaceError


class MemoryStorage:
    """
    Simple in-memory temp storage.
    Keeps only references to objects and does not copy them.
    Automatically trims storage according to the `max_capacity`.
    """

    def __init__(
        self, max_capacity: int, min_persist_time: int = 60, headroom_percent: int = 10
    ) -> None:
        """
        Args:
            `max_capacity`: Storage size in bytes
            `min_persist_time`: Minimum span of time which the objects are kept
                                before getting trimmed
            `headroom_percent`: Percentage of storage size to trim in advance.
        """
        self.__max_capacity = max_capacity
        self.__min_persist_time = min_persist_time
        self.__headroom_percent = headroom_percent

        self.__current_size = 0
        self.__store = {}  # Actual stored objects

        # Priority queues for different categories (min heaps)
        self.__expired_done_with = []  # Priority 1: Expired items with done_with=True
        self.__expired_not_done = []  # Priority 2: Expired items with done_with=False
        self.__not_expired_done_with = (
            []
        )  # Priority 3: Non-expired items with done_with=True
        self.__not_expired_not_done = (
            []
        )  # Not for trimming: Non-expired items with done_with=False

        # Maps key to its category and timestamp for quick lookups and updates
        self.__key_metadata = {}  # {key: (category_index, timestamp)}

        self.__data_lock = asyncio.Lock()

    async def store(self, value) -> str | None:
        """
        Args:
            `value`: The object to be stored
        Returns:
            str: Stored object access key
            None: Failed to store the object
        """
        # Calculate the size of the object in memory
        value_size = sys.getsizeof(value)

        # Trim storage if needed before adding new item
        async with self.__data_lock:
            await self.__trim(value_size)

        key = str(uuid.uuid4())

        async with self.__data_lock:
            current_time = int(time.time())

            self.__store[key] = {
                "value": value,
                "size": value_size,
                "last_used": current_time,
                "done_with": False,
            }

            # Add to the appropriate heap (not expired, not done with)
            heapq.heappush(self.__not_expired_not_done, (current_time, key))
            self.__key_metadata[key] = (
                3,
                current_time,
            )  # Category 3 = not_expired_not_done

            self.__current_size += value_size

        return key

    async def donewith(self, key: str) -> None:
        async with self.__data_lock:
            if key not in self.__store:
                return

            self.__store[key]["done_with"] = True

            # Move the item to the appropriate category
            await self.__update_item_category(key)

    async def retrieve(self, key: str):
        async with self.__data_lock:
            if key not in self.__store:
                return None

            # Get the stored item
            item = self.__store[key]

            # Update the last used time
            current_time = int(time.time())
            item["last_used"] = current_time
            item["done_with"] = False

            # Remove from old category and add to new one
                # We don't physically remove from the old heap as it would be O(n)
                # Instead, we'll mark it as invalid by updating the metadata

            # Add to not_expired_not_done category
            heapq.heappush(self.__not_expired_not_done, (current_time, key))
            self.__key_metadata[key] = (
                3,
                current_time,
            )  # Category 3 = not_expired_not_done

            return item["value"]

    async def purge(self) -> None:
        async with self.__data_lock:
            self.__store.clear()
            self.__expired_done_with.clear()
            self.__expired_not_done.clear()
            self.__not_expired_done_with.clear()
            self.__not_expired_not_done.clear()
            self.__key_metadata.clear()
            self.__current_size = 0

    async def consumed_size(self) -> int:
        async with self.__data_lock:
            return self.__current_size

    async def __update_item_category(self, key: str) -> None:
        """Update an item's category based on its current state."""
        if key not in self.__store or key not in self.__key_metadata:
            return

        item = self.__store[key]
        current_time = int(time.time())
        is_expired = current_time - item["last_used"] >= self.__min_persist_time
        is_done_with = item["done_with"]

        # Determine the new category
        if is_expired and is_done_with:
            new_category = 0  # expired_done_with
            target_heap = self.__expired_done_with
        elif is_expired:
            new_category = 1  # expired_not_done
            target_heap = self.__expired_not_done
        elif is_done_with:
            new_category = 2  # not_expired_done_with
            target_heap = self.__not_expired_done_with
        else:
            new_category = 3  # not_expired_not_done
            target_heap = self.__not_expired_not_done

        # Add to the new category heap
        timestamp = item["last_used"]
        heapq.heappush(target_heap, (timestamp, key))
        self.__key_metadata[key] = (new_category, timestamp)

    async def __check_expired_items(self) -> None:
        """Check for items that have expired and move them to the appropriate category."""
        current_time = int(time.time())
        keys_to_update = []

        # Check not_expired_done_with for items that might have expired
        for timestamp, key in self.__not_expired_done_with:
            if key in self.__store and key in self.__key_metadata:
                category, stored_time = self.__key_metadata[key]
                if (
                    category == 2 and stored_time == timestamp
                ):  # Valid entry in not_expired_done_with
                    if current_time - timestamp >= self.__min_persist_time:
                        keys_to_update.append(key)  # This item has expired

        # Check not_expired_not_done for items that might have expired
        for timestamp, key in self.__not_expired_not_done:
            if key in self.__store and key in self.__key_metadata:
                category, stored_time = self.__key_metadata[key]
                if (
                    category == 3 and stored_time == timestamp
                ):  # Valid entry in not_expired_not_done
                    if current_time - timestamp >= self.__min_persist_time:
                        keys_to_update.append(key)  # This item has expired

        # Update categories for expired items
        for key in keys_to_update:
            await self.__update_item_category(key)

    async def __trim(self, needed_size: int = 0) -> None:
        if self.__current_size + needed_size <= self.__max_capacity:
            # There is already enough space
            return

        headroom = self.__max_capacity / 100 * self.__headroom_percent
        try_to_free = self.__current_size - self.__max_capacity + headroom
        min_space_to_free = self.__current_size - self.__max_capacity + needed_size
        freed = 0

        # First, update expired status of items
        await self.__check_expired_items()

        # Try to free up space by removing items in priority order
        for priority_queue in [
            self.__expired_done_with,
            self.__expired_not_done,
            self.__not_expired_done_with,
        ]:
            while (
                priority_queue
                and self.__current_size + needed_size > self.__max_capacity
            ):
                timestamp, key = heapq.heappop(priority_queue)

                # Check if this entry is still valid
                if key not in self.__key_metadata:
                    continue

                category_index, stored_time = self.__key_metadata[key]
                category_queues = [
                    self.__expired_done_with,
                    self.__expired_not_done,
                    self.__not_expired_done_with,
                    self.__not_expired_not_done,
                ]

                # Only process if this is a valid entry (matches current category and timestamp)
                if (
                    category_queues[category_index] != priority_queue
                    or stored_time != timestamp
                ):
                    continue

                if key not in self.__store:
                    continue

                item_size = self.__store[key]["size"]
                self.__current_size -= item_size
                freed += item_size
                del self.__store[key]
                del self.__key_metadata[key]

                if freed >= try_to_free:
                    return

        if freed >= min_space_to_free:
            return

        raise NotEnoughSpaceError(f"needed {needed_size} bytes")
