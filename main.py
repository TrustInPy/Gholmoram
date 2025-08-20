import logsetup
import asyncio
import envs
import logging
import features
from bot import client, cycle_connection_method, con_fail_meter
from envs import BOT_TOKEN, EXIT_ON_DISCONNECTION_LOOP
from features import activate_features, tasks_init_loop

_logger = logging.getLogger("main")


def main():
    _logger.info("main: Starting main")
    _logger.info("main: Activating features")
    client.loop.create_task(activate_features())
    _logger.info("main: Running features tasks initiator loop")
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
            pass
        finally:
            _logger.warning("main: Bot lost connection.")
            try:
                client.disconnect()
            except:
                pass
            if EXIT_ON_DISCONNECTION_LOOP:
                if con_fail_meter.trigger():
                    _logger.error("main: Failed connection attempts exceeded the limit")
                    break
            cycle_connection_method()

    # Execute graceful exit procedure


if __name__ == "__main__":
    main()
