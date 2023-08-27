from bot import client
from telethon.sync import events
from telethon import functions, types


teammates = [
    {
        "name": "Ali",
        "access_hash": -1344560218691266120,
        "user_id": 593951783,
    },
    {
        "name": "Sina",
        "access_hash": -4572404436797027872,
        "user_id": 1465986382,
    },
    {
        "name": "Ehsan",
        "access_hash": 7275169862155910271,
        "user_id": 96648148,
    },
    {
        "name": "Bagher",
        "access_hash": 7661763894202739702,
        "user_id": 349220992,
    },
    {
        "name": "Hossein",
        "access_hash": -4167431907308019128,
        "user_id": 590659925,
    },
    {
        "name": "Hossein(Moz)",
        "access_hash": 8432150841221988794,
        "user_id": 137423245,
    },
]


@client.on(
    events.NewMessage(func=lambda e: e.is_group or e.is_private, pattern="(?i)/team")
)
async def team(event):
    message_chat_id = event.chat_id
    try:
        users = None
        try:
            users = await client(
                functions.users.GetUsersRequest(
                    [
                        types.InputUser(
                            teammates[0]["user_id"], teammates[0]["access_hash"]
                        ),
                        types.InputUser(
                            teammates[1]["user_id"], teammates[1]["access_hash"]
                        ),
                        types.InputUser(
                            teammates[2]["user_id"], teammates[2]["access_hash"]
                        ),
                        types.InputUser(
                            teammates[3]["user_id"], teammates[3]["access_hash"]
                        ),
                        types.InputUser(
                            teammates[4]["user_id"], teammates[4]["access_hash"]
                        ),
                        types.InputUser(
                            teammates[5]["user_id"], teammates[5]["access_hash"]
                        ),
                    ]
                )
            )
        except Exception as e:
            pass
        if users:
            team_members = "🔅 Bunch of friends gathered together as a team:\n\n"
            for i in range(len(users)):
                user = users[i]
                if user.username:
                    team_members = (
                        team_members
                        + f"🔸 [{teammates[i]['name']}](t.me/{user.username})\n"
                    )
                else:
                    team_members = team_members + f"🔸 {teammates[i]['name']}\n"
        else:
            team_members = "🔅 Bunch of friends gathered together as a team:\n\n"
            for i in range(len(teammates)):
                team_members = team_members + f"🔸 {teammates[i]['name']}\n"

        await client.send_message(message_chat_id, team_members, link_preview=False)
    except Exception as e:
        print("Team " + str(e))
