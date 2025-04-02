import logging
import re
from envs import SESSION_NAME, APP_API_ID, APP_API_HASH, PROXY, BACKUP_PROXY
from telethon.sync import TelegramClient

_logger = logging.getLogger("main")

client = TelegramClient(SESSION_NAME, APP_API_ID, APP_API_HASH, connection_retries=2)

proxy_regex = r"^(?P<protocol>http|https|socks5)://(?:(?P<username>[^:@]+)(?::(?P<password>[^:@]*))?@)?(?P<host>[\w.-]+|\d{1,3}(?:\.\d{1,3}){3})(?::(?P<port>\d+))?$"


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


def set_no_proxy():
    client._proxy = None
    _logger.info("bot: Using NO proxy for the client.")


def set_proxy():
    client._proxy = _proxy_dict
    _logger.info("bot: Using proxy for the client.")


def set_backup_proxy():
    client._proxy = _backup_proxy_dict
    _logger.info("bot: Using backup proxy for the client.")


def cycle_connection_method():
    global _state
    _logger.info("bot: Trying to change the connection method...")

    if _state is None:
        if PROXY:
            _state = "proxy"
            set_proxy()
        else:
            _state = "direct"
            set_no_proxy()

    elif _state == "direct":
        if BACKUP_PROXY:
            _state = "backup_proxy"
            set_backup_proxy()

    elif _state == "proxy":
        if BACKUP_PROXY:
            _state = "backup_proxy"
            set_backup_proxy()

    elif _state == "backup_proxy":
        if PROXY:
            _state = "proxy"
            set_proxy()
        else:
            _state = "direct"
            set_no_proxy()


def _init():
    global _state, _proxy_dict, _backup_proxy_dict
    _state = None
    _proxy_dict = extract_proxy(PROXY)
    _backup_proxy_dict = extract_proxy(BACKUP_PROXY)
    cycle_connection_method()


if "_initialized" not in dir():  # Run once
    global _initialized
    _init()
    _initialized = True
