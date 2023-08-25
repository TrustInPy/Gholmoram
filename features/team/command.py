from bot import *
from telethon.sync import events


@client.on(
    events.NewMessage(func=lambda e: e.is_group or e.is_private, pattern="(?i)/team")
)
async def team(event):
    message_chat_id = event.chat_id
    try:
        team = (
            "🔅 Bunch of friends gathered together as a team:\n\n"
            + "🔸 [@Ali](tg://user?id=593951783)\n"
            + "🔸 [@Sina](tg://user?id=1465986382)\n"
            + "🔸 [@Ehsan](tg://user?id=96648148)\n"
            + "🔸 [@Bagher](tg://user?id=349220992)\n"
            + "🔸 [@Hossein](tg://user?id=590659925)\n"
            + "🔸 [@Hossein(Moz)](tg://user?id=137423245)\n"
        )
        await client.send_message(message_chat_id, team)
    except Exception as e:
        print("Team" + str(e))
