import json
from datetime import datetime
import aiosqlite
import aiohttp
from bot import DATABASE_NAME


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
