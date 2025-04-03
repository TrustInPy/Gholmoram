import dotenv
import os


def _init():
    global APP_API_ID, APP_API_HASH, BOT_TOKEN, SESSION_NAME, ADMIN_ID
    global BOT_ALLOW_NO_PROXY, BOT_PROXY_LIST
    global FEATURE_ALLOW_NO_PROXY, FEATURE_PROXY_LIST
    global MAX_CACHE_SIZE

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
    MAX_CACHE_SIZE = "50M"

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
        ADMIN_ID = os.getenv("ADMIN_ID")

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

    if os.getenv("MAX_CACHE_SIZE"):
        MAX_CACHE_SIZE = os.getenv("MAX_CACHE_SIZE")


if "_initialized" not in dir():  # Run once
    global _initialized
    _init()
    _initialized = True
