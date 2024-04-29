import re
import os
import sys
import json
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
IR_PROXY = os.getenv("IR_PROXY")
PROXY = os.getenv("PROXY")

client = TelegramClient("Gholmoram", API_ID, API_HASH, connection_retries=0)
client.parse_mode = "md"

ip_reg = r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\:(\d{1,5})$"


def validate_proxy(proxy):
    if not re.match(ip_reg, proxy):
        print(f"Wrong format of {proxy} in .env file.")
        sys.exit()

if PROXY:
    validate_proxy(PROXY)
    IP = PROXY.split(":")[0]
    PORT = PROXY.split(":")[1]
else:
    IP = '127.0.0.2' # :)
    PORT = '1000'


if IR_PROXY:
    validate_proxy(IR_PROXY)
    proxies = {
        "http": f"http://{IR_PROXY}",
        "https": f"http://{IR_PROXY}",
    }
else:
    print("WARNING! Some of the features may not work properly without IR_PROXY")
    proxies = None

def switch_to_proxy():
    client._proxy = ("socks5", IP, int(PORT), True)


def reset_client():
    client._proxy = None
