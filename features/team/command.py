from bot import *

@client.on(events.NewMessage(func=lambda e: e.is_group, pattern="(?i)/team"))
async def team(event):
    if event.chat_id in HOME:
        message_chat_id = event.chat_id

        try:
            team = (
                "🔰 Bunch of friends gathered together "
                + "as a team:\n\n👨‍💻 Ehsan \n💃 Hossein(Moz) \n🫰 Bagher \n🪡 Hossein(Defalcator) \n🪃 Ali \n🧻 Sina "
            )
            await client.send_message(message_chat_id, team)
        except Exception as e:
            print("Team" + str(e))

    else:
        pass
