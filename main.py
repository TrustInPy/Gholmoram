import features
from bot import *
from task import starter

client.start()
print("Bot started... ")

client.loop.run_until_complete(starter())
client.run_until_disconnected()
