import event
import features
from bot import client
from task import starter
from data.database import run_database


# Run the database setup asynchronously
async def setup_database():
    await run_database()


# Start the bot and run database setup
async def main():
    await setup_database()
    await starter()

    print("--------------------------------------------------------")
    print("Database ready +++")


# Start the bot client and other setup
client.loop.run_until_complete(main())

client.start()
print("--------------------------------------------------------")
print("Bot started... ")

client.run_until_disconnected()
