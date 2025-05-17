import logsetup
import asyncio
import envs
import logging
import features
from bot import client, cycle_connection_method
from envs import BOT_TOKEN
from features import tasks_init_loop

_logger = logging.getLogger("main")


def main():
    client.loop.create_task(tasks_init_loop())
    while True:
        try:
            _logger.info("main: Starting bot...")
            client.start(bot_token=BOT_TOKEN)
            _logger.info("main: Bot connected.")
            client.run_until_disconnected()
        except KeyboardInterrupt:
            break
        except:
            _logger.info("main: Bot lost connection.")
            try:
                client.disconnect()
            except:
                pass
            cycle_connection_method()


if __name__ == "__main__":
    main()
