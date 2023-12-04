import os
import json
import socks
from dotenv import load_dotenv
from telethon.sync import TelegramClient

load_dotenv()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
HOME_ID = int(os.getenv("HOME_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
DATABASE_NAME = os.getenv("DATABASE_NAME")
INSTA_USERNAME = os.getenv("INSTA_USERNAME")
INSTA_PASSWORD = os.getenv("INSTA_PASSWORD")

proxies = {
    "http":"http://127.0.0.1:1071",
    "https":"http://127.0.0.1:1071",
}

client = TelegramClient("Gholmoram", API_ID, API_HASH, proxy=("socks5", "127.0.0.1", 10808, True))
client.parse_mode = "md"
