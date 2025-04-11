_FEATURE_NAME = "hafez"

import logging

_logger = logging.getLogger("main")


if "_active" not in dir():  # Run once
    global _active
    _active = False


def is_active():
    return _active


def activate():
    global _active
    if is_active():
        return
    _active = True
    _logger.debug(f"features: Feature has been activated: '{_FEATURE_NAME}'")


from . import event


async def task_runner():
    if not is_active():
        return
    pass
