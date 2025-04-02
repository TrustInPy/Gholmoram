import dotenv
import os


def _init():
    global APP_API_ID, APP_API_HASH, BOT_TOKEN, SESSION_NAME
    global ADMIN_ID, PROXY, BACKUP_PROXY, MAX_CACHE_SIZE

    # Default values
    APP_API_ID = None
    APP_API_HASH = None
    BOT_TOKEN = None
    SESSION_NAME = "gholmoram"
    ADMIN_ID = None
    PROXY = None
    BACKUP_PROXY = None
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
    if os.getenv("PROXY"):
        PROXY = os.getenv("PROXY")
    if os.getenv("BACKUP_PROXY"):
        BACKUP_PROXY = os.getenv("BACKUP_PROXY")
    if os.getenv("MAX_CACHE_SIZE"):
        MAX_CACHE_SIZE = os.getenv("MAX_CACHE_SIZE")


if "_initialized" not in dir():  # Run once
    global _initialized
    _init()
    _initialized = True
