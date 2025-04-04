import json
import logging
import re
from envs import FEATURE_ALLOW_NO_PROXY, FEATURE_PROXY_LIST

_logger = logging.getLogger("main")

proxy_regex = r"^(?P<protocol>http|https|socks5)://(?:(?P<username>[^:@]+)(?::(?P<password>[^:@]*))?@)?(?P<host>[\w.-]+|\d{1,3}(?:\.\d{1,3}){3})(?::(?P<port>\d+))?$"

proxy_dict_list = []
proxy_str_list = []


def _validate_proxy(proxy_str: str) -> bool:
    return re.match(proxy_regex, proxy_str)


def _extract_proxy(proxy_str: str) -> dict:
    if not proxy_str:
        return None

    # Extract components using regex
    match = re.match(proxy_regex, proxy_str)
    if not match:
        _logger.error(f"features: Invalid proxy format: {proxy_str}")
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


def _init():
    global proxy_dict_list, proxy_str_list
    if not FEATURE_PROXY_LIST:
        proxy_dict_list = []
    else:
        proxies = json.loads(FEATURE_PROXY_LIST)
        for proxy_str in proxies:
            if _validate_proxy(proxy_str):
                proxy_str_list.append(proxy_str)
                proxy_dict_list.append(_extract_proxy(proxy_str))


if "_initialized" not in dir():  # Run once
    global _initialized
    _init()
    _initialized = True
