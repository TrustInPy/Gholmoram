import time
import event
import features
from task import starter
from data.database import run_database
from bot import client, switch_to_proxy, reset_client


# Run the database setup asynchronously
async def setup_database():
    await run_database()


# Start the bot and run database setup
async def main():
    await setup_database()
    await starter()

    print("--------------------------------------------------------")
    print("Database ready +++")


proxy_switch = False

while True:
    try:
        # Start the bot client and other setup
        client.start()
        print("\n" + "--------------------------------------------------------")
        print(f"Bot started in {proxy_switch} proxy mode.")
        print("--------------------------------------------------------" + "\n")

        client.loop.run_until_complete(main())

        client.run_until_disconnected()

    except ConnectionError as e:
        (
            (switch_to_proxy(), proxy_switch := True)
            if not proxy_switch
            else (reset_client(), proxy_switch := False)
        )
        time.sleep(10)
        pass
