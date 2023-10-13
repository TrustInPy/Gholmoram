import json
import aiosqlite
import aiohttp
from bot import client, DATABASE_NAME
from datetime import datetime


async def get_free_games_links():
    try:
        url = (
            f"https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US&"
            f"spaceId=1af6c7f8a3624b1788eaf23175fdd16f&"
            f"redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fstore%2Fen-US%2F&"
            f"key=da1563f4abe7480fb43364b7d30d9a7b&"
            f"promoId=freegames"
        )
        raw_response = None
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Get response status was {response.status}")
                raw_response = await response.content.read()
        response_json = json.loads(raw_response)

        for game in response_json["data"]["Catalog"]["searchStore"]["elements"]:
            if game["price"]["totalPrice"]["discountPrice"] != 0:
                continue

            try:
                slug = None
                try:
                    slug = game["productSlug"]
                except Exception:
                    pass
                try:
                    slug = game["catalogNs"]["mappings"][0]["pageSlug"]
                except Exception:
                    pass

                if not game["promotions"]:
                    continue

                if not game["promotions"]["promotionalOffers"]:
                    continue

                end_date = datetime.strptime(
                    game["promotions"]["promotionalOffers"][0]["promotionalOffers"][0][
                        "endDate"
                    ],
                    "%Y-%m-%dT%H:%M:%S.%fZ",
                )

                if not slug or not game["title"]:
                    continue

                game_name = game["title"]

                if game["offerType"] == "BUNDLE":
                    game_link = (
                        f"https://launcher.store.epicgames.com/en-US/bundles/{slug}"
                    )
                else:
                    game_link = f"https://launcher.store.epicgames.com/en-US/p/{slug}"

                try:
                    conn = await aiosqlite.connect(DATABASE_NAME)

                    cursor = await conn.cursor()

                    query = """
                        INSERT OR REPLACE INTO free_games
                        (name, end_date, url)
                        SELECT ?, ?, ? WHERE NOT EXISTS (
                            SELECT * FROM free_games WHERE name = ? AND end_date = ?
                        )
                        """

                    await cursor.execute(
                        query,
                        (
                            game_name,
                            end_date,
                            game_link,
                            game_name,
                            end_date,
                        ),
                    )
                    await conn.commit()
                    await conn.close()
                except Exception as e:
                    print("Failed to add new free games to database.")
                    print(e)

            except Exception as e:
                print(
                    "features/epic_games: There is a broken Epic Games link: " + str(e)
                )

    except:
        print("features/epic_games: Failed to get free games list from Epic Games.")


async def send_valid_links_to_chats(client, DATABASE_NAME):
    try:
        epic_conn = await aiosqlite.connect(DATABASE_NAME)

        cursor = await epic_conn.cursor()
        current_date = datetime.now()

        query = f"""
            SELECT * FROM free_games
            WHERE end_date >= ?
            """
        await cursor.execute(query, (current_date,))
        free_games = await cursor.fetchall()

        query = f"""
            SELECT * FROM chats
            WHERE epic_notification = 1
            """
        await cursor.execute(query)
        chats = await cursor.fetchall()

        for chat in chats:
            chat_id = chat[0]
            for game in free_games:
                game_id = game[0]
                game_name = game[1]
                end_date = datetime.strptime(game[2], "%Y-%m-%d %H:%M:%S")
                game_link = game[3]

                end_date_str = end_date.strftime("%Y-%m-%d %H:%M")

                message = (
                    f"💎 **{game_name}** is free\n"
                    f"⏳ until **{end_date_str}**\n"
                    f"----------------------------------------\n"
                    f"👇🏻Get it here: {game_link}\n"
                    f"----------------------------------------\n"
                )

                result = await cursor.execute(
                    """
                    SELECT * FROM url_chat WHERE chat_id = ? AND game_id = ?
                    """,
                    (chat_id, game_id),
                )
                data = await result.fetchone()
                if data is None:
                    await client.send_message(chat_id, message)
                    await cursor.execute(
                        """
                        INSERT INTO url_chat (chat_id, game_id) VALUES (?, ?)
                        """,
                        (chat_id, game_id),
                    )
                    await epic_conn.commit()

        await epic_conn.close()
    except Exception as e:
        print("Failed to get free games from database.\n" + str(e))


async def toggle_epic_notification(chat_id):
    conn = await aiosqlite.connect(DATABASE_NAME)
    cursor = await conn.cursor()

    await cursor.execute(
        "SELECT epic_notification FROM chats WHERE chat_id = ?", (chat_id,)
    )
    result = await cursor.fetchone()
    current_value = result[0] if result else None

    if current_value == 1:
        new_value = 0
    else:
        new_value = 1

    await cursor.execute(
        "UPDATE chats SET epic_notification = ? WHERE chat_id = ?", (new_value, chat_id)
    )
    await conn.commit()
    if new_value == 1:
        await send_valid_links_to_chats(client, DATABASE_NAME)

    await conn.close()
