_FEATURE_NAME = "base"

import logging

_logger = logging.getLogger("main")


if "_active" not in dir():  # Run once
    global _active
    _active = False


def is_active():
    return _active


def activate():
    global _active
    _active = True
    _logger.debug(f"features: Feature has been activated: '{_FEATURE_NAME}'")


async def task_runner():
    if not is_active():
        return
    pass
