import dotenv
import logging
import os
import re

_logger = logging.getLogger("main")


def _init():
    global APP_API_ID, APP_API_HASH, BOT_TOKEN, SESSION_NAME, ADMIN_ID
    global BOT_ALLOW_NO_PROXY, BOT_PROXY_LIST
    global FEATURE_ALLOW_NO_PROXY, FEATURE_PROXY_LIST
    global INSTADL_COBALT_API_URL, MAX_MEM_CACHE_SIZE, MAX_DISK_CACHE_SIZE

    # Default values
    APP_API_ID = None
    APP_API_HASH = None
    BOT_TOKEN = None
    SESSION_NAME = "gholmoram"
    ADMIN_ID = None
    BOT_ALLOW_NO_PROXY = True
    BOT_PROXY_LIST = None
    FEATURE_ALLOW_NO_PROXY = True
    FEATURE_PROXY_LIST = None
    INSTADL_COBALT_API_URL = None
    MAX_MEM_CACHE_SIZE = 100 * 2**20  # 100 MiB
    MAX_DISK_CACHE_SIZE = 2 * 2**30  # 2 GiB

    dotenv.load_dotenv()

    if os.getenv("APP_API_ID"):
        APP_API_ID = os.getenv("APP_API_ID")

    if os.getenv("APP_API_HASH"):
        APP_API_HASH = os.getenv("APP_API_HASH")

    if os.getenv("BOT_TOKEN"):
        BOT_TOKEN = os.getenv("BOT_TOKEN")

    if os.getenv("SESSION_NAME"):
        SESSION_NAME = os.getenv("SESSION_NAME")

    if os.getenv("ADMIN_ID"):
        ADMIN_ID = int(os.getenv("ADMIN_ID"))

    if os.getenv("BOT_ALLOW_NO_PROXY"):
        if os.getenv("BOT_ALLOW_NO_PROXY").lower() in ["1", "true", "yes", "y"]:
            BOT_ALLOW_NO_PROXY = True
        elif os.getenv("BOT_ALLOW_NO_PROXY").lower() in ["0", "false", "no", "n"]:
            BOT_ALLOW_NO_PROXY = False

    if os.getenv("BOT_PROXY_LIST"):
        BOT_PROXY_LIST = os.getenv("BOT_PROXY_LIST")

    if os.getenv("FEATURE_ALLOW_NO_PROXY"):
        if os.getenv("FEATURE_ALLOW_NO_PROXY").lower() in ["1", "true", "yes", "y"]:
            FEATURE_ALLOW_NO_PROXY = True
        elif os.getenv("FEATURE_ALLOW_NO_PROXY").lower() in ["0", "false", "no", "n"]:
            FEATURE_ALLOW_NO_PROXY = False

    if os.getenv("FEATURE_PROXY_LIST"):
        FEATURE_PROXY_LIST = os.getenv("FEATURE_PROXY_LIST")

    if os.getenv("INSTADL_COBALT_API_URL"):
        INSTADL_COBALT_API_URL = os.getenv("INSTADL_COBALT_API_URL")

    if os.getenv("MAX_MEM_CACHE_SIZE"):
        size_str = os.getenv("MAX_MEM_CACHE_SIZE")
        match = re.match(r"^(?P<value>\d+(\.\d+)?)(?P<unit>[kKmMgGtTpP]?)$", size_str)
        if not match:
            _logger.error(f"envs: Invalid size format: {size_str}")
            raise ValueError("Invalid size format.")

        value = float(match.group("value"))
        unit = match.group("unit").lower()

        if unit == "k":
            size = value * 2**10
        elif unit == "m":
            size = value * 2**20
        elif unit == "g":
            size = value * 2**30
        elif unit == "t":
            size = value * 2**40
        elif unit == "p":
            size = value * 2**50
        else:
            size = value  # No unit means exact byte amount

        MAX_MEM_CACHE_SIZE = int(size)

    if os.getenv("MAX_DISK_CACHE_SIZE"):
        size_str = os.getenv("MAX_DISK_CACHE_SIZE")
        match = re.match(r"^(?P<value>\d+(\.\d+)?)(?P<unit>[kKmMgGtTpP]?)$", size_str)
        if not match:
            _logger.error(f"envs: Invalid size format: {size_str}")
            raise ValueError("Invalid size format.")

        value = float(match.group("value"))
        unit = match.group("unit").lower()

        if unit == "k":
            size = value * 2**10
        elif unit == "m":
            size = value * 2**20
        elif unit == "g":
            size = value * 2**30
        elif unit == "t":
            size = value * 2**40
        elif unit == "p":
            size = value * 2**50
        else:
            size = value  # No unit means exact byte amount

        MAX_DISK_CACHE_SIZE = int(size)


if "_initialized" not in dir():  # Run once
    global _initialized
    _init()
    _initialized = True
