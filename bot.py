import os
import json
from dotenv import load_dotenv
from telethon import TelegramClient, events, client



load_dotenv()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
HOME = json.loads(os.getenv("HOME"))

client = TelegramClient('name', API_ID, API_HASH)