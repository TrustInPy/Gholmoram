import dotenv
import logging
import os
from datetime import datetime


def _init():
    global LOG_SAVE_ROOT, LOG_MAIN_TO_CONSOLE, LOG_ROOT_TO_CONSOLE
    global LOG_LEVEL, LOG_LEVEL_MAIN, LOG_LEVEL_ROOT, LOG_LEVEL_CONSOLE

    # default settings:
    LOG_SAVE_ROOT = True
    LOG_MAIN_TO_CONSOLE = False
    LOG_ROOT_TO_CONSOLE = True
    LOG_LEVEL = logging.DEBUG
    LOG_LEVEL_MAIN = LOG_LEVEL
    LOG_LEVEL_ROOT = LOG_LEVEL
    LOG_LEVEL_CONSOLE = LOG_LEVEL

    dotenv.load_dotenv()

    _LOG_SAVE_ROOT = os.getenv("LOG_SAVE_ROOT")
    if _LOG_SAVE_ROOT:
        if _LOG_SAVE_ROOT.lower() in ["1", "true", "yes", "y"]:
            LOG_SAVE_ROOT = True
        elif _LOG_SAVE_ROOT.lower() in ["0", "false", "no", "n"]:
            LOG_SAVE_ROOT = False

    _LOG_MAIN_TO_CONSOLE = os.getenv("LOG_MAIN_TO_CONSOLE")
    if _LOG_MAIN_TO_CONSOLE:
        if _LOG_MAIN_TO_CONSOLE.lower() in ["1", "true", "yes", "y"]:
            LOG_MAIN_TO_CONSOLE = True
        elif _LOG_MAIN_TO_CONSOLE.lower() in ["0", "false", "no", "n"]:
            LOG_MAIN_TO_CONSOLE = False

    _LOG_ROOT_TO_CONSOLE = os.getenv("LOG_ROOT_TO_CONSOLE")
    if _LOG_ROOT_TO_CONSOLE:
        if _LOG_ROOT_TO_CONSOLE.lower() in ["1", "true", "yes", "y"]:
            LOG_ROOT_TO_CONSOLE = True
        elif _LOG_ROOT_TO_CONSOLE.lower() in ["0", "false", "no", "n"]:
            LOG_ROOT_TO_CONSOLE = False

    LOG_LEVEL = _parse_log_level(os.getenv("LOG_LEVEL"))
    LOG_LEVEL_MAIN = _parse_log_level(os.getenv("LOG_LEVEL_MAIN"))
    LOG_LEVEL_ROOT = _parse_log_level(os.getenv("LOG_LEVEL_ROOT"))
    LOG_LEVEL_CONSOLE = _parse_log_level(os.getenv("LOG_LEVEL_CONSOLE"))

    # Setup logging
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if not os.path.exists("./logs/"):
        os.makedirs("./logs/")
    log_formatter = logging.Formatter(
        "%(asctime)s | %(name)-4.4s | %(threadName)-16.16s | %(levelname)-8.8s | %(message)s"
    )

    #### main logs
    main_logger = logging.getLogger("main")
    main_logger.setLevel(LOG_LEVEL_MAIN)
    main_logger.handlers.clear()

    # log to console
    if LOG_MAIN_TO_CONSOLE:
        main_console_handler = logging.StreamHandler()
        main_console_handler.setLevel(LOG_LEVEL_CONSOLE)
        main_console_handler.setFormatter(log_formatter)
        main_logger.addHandler(main_console_handler)

    # log to file
    main_file_handler = logging.FileHandler(
        f"logs/{date_str}_main.log", encoding="utf-8"
    )
    main_file_handler.setLevel(LOG_LEVEL_MAIN)
    main_file_handler.setFormatter(log_formatter)
    main_logger.addHandler(main_file_handler)

    #### root logs (all loggers combined)
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL_ROOT)
    root_logger.handlers.clear()

    # log to console
    if LOG_ROOT_TO_CONSOLE:
        root_console_handler = logging.StreamHandler()
        root_console_handler.setLevel(LOG_LEVEL_CONSOLE)
        root_console_handler.setFormatter(log_formatter)
        root_logger.addHandler(root_console_handler)

    # log to file
    if LOG_SAVE_ROOT:
        root_file_handler = logging.FileHandler(
            f"logs/{date_str}_root.log", encoding="utf-8"
        )
        root_file_handler.setLevel(LOG_LEVEL_ROOT)
        root_file_handler.setFormatter(log_formatter)
        root_logger.addHandler(root_file_handler)


def _parse_log_level(level: str):
    if not level:
        return LOG_LEVEL

    level = level.upper()
    if level == "CRITICAL":
        return logging.CRITICAL
    if level == "FATAL":
        return logging.FATAL
    if level == "ERROR":
        return logging.ERROR
    if level == "WARN":
        return logging.WARN
    if level == "WARNING":
        return logging.WARNING
    if level == "INFO":
        return logging.INFO
    if level == "DEBUG":
        return logging.DEBUG
    if level == "NOTSET":
        return logging.NOTSET

    return LOG_LEVEL


if "_initialized" not in dir():  # Run once
    global _initialized
    _init()
    _initialized = True
