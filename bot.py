import json
import logging
import re
from envs import (
    SESSION_NAME,
    APP_API_ID,
    APP_API_HASH,
    BOT_ALLOW_NO_PROXY,
    BOT_PROXY_LIST,
)
from telethon import TelegramClient

_logger = logging.getLogger("main")

client = TelegramClient(
    SESSION_NAME, APP_API_ID, APP_API_HASH, connection_retries=0, timeout=5
)

proxy_regex = r"^(?P<protocol>http|https|socks5)://(?:(?P<username>[^:@]+)(?::(?P<password>[^:@]*))?@)?(?P<host>[\w.-]+|\d{1,3}(?:\.\d{1,3}){3})(?::(?P<port>\d+))?$"

proxy_list = []
active_proxy_index = None


def extract_proxy(proxy_str: str) -> dict:
    if not proxy_str:
        return None

    # Extract components using regex
    match = re.match(proxy_regex, proxy_str)
    if not match:
        _logger.error(f"bot: Invalid proxy format: {proxy_str}")
        raise ValueError("Invalid proxy format.")

    # Create proxy dictionary
    proxy_template = {
        "proxy_type": match.group("protocol"),
        "addr": match.group("host"),
        "port": int(match.group("port")),
        "rdns": True,
    }

    # Include username and password if provided
    if match.group("username"):
        proxy_template["username"] = match.group("username")
    if match.group("password"):
        proxy_template["password"] = match.group("password")

    return proxy_template


def cycle_connection_method(first_run: bool = False):
    global active_proxy_index
    if first_run:
        if BOT_ALLOW_NO_PROXY:
            active_proxy_index = None
            client._proxy = None
            _logger.info("bot: Using NO proxy for the client.")
            return

    _logger.info("bot: Trying to change the connection method...")

    if len(proxy_list) == 0:
        if BOT_ALLOW_NO_PROXY:
            client._proxy = None
            _logger.info("bot: There is no proxy to try. Continuing with no proxy...")
            return
        else:
            raise Exception("No connection methods to try!")

    if active_proxy_index is None:
        active_proxy_index = 0
    else:
        active_proxy_index += 1
        if active_proxy_index >= len(proxy_list):
            if BOT_ALLOW_NO_PROXY:
                active_proxy_index = None
            else:
                active_proxy_index = 0

    if active_proxy_index is None:
        client._proxy = None
        _logger.info("bot: Using NO proxy for the client.")
    else:
        client._proxy = proxy_list[active_proxy_index]
        _logger.info(f"bot: Using proxy at index {active_proxy_index} for the client.")


def _init():
    global proxy_list
    if not BOT_PROXY_LIST:
        proxy_list = []
    else:
        proxy_str_list = json.loads(BOT_PROXY_LIST)
        for proxy_str in proxy_str_list:
            proxy_list.append(extract_proxy(proxy_str))

    cycle_connection_method(first_run=True)


if "_initialized" not in dir():  # Run once
    global _initialized
    _init()
    _initialized = True
