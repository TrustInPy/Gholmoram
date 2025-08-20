# Load Proxies
from . import proxies
from utilities import web_helper

web_helper.set_proxies(proxies.proxy_str_list, proxies.FEATURE_ALLOW_NO_PROXY)


# Activate features
from . import about
from . import base
from . import hafez
from . import hekmat
from . import id
from . import insta_dl
from . import mention_all


async def activate_features():
    about.activate()
    base.activate()
    hafez.activate()
    hekmat.activate()
    id.activate()
    await insta_dl.activate()
    mention_all.activate()


# Scheduled Tasks
import asyncio
from bot import client


async def tasks_init_loop():
    while True:
        # Call individual features task runners
        client.loop.create_task(base.task_runner())
        client.loop.create_task(about.task_runner())
        client.loop.create_task(hafez.task_runner())
        client.loop.create_task(id.task_runner())
        client.loop.create_task(insta_dl.task_runner())
        await asyncio.sleep(1)
