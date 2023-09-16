import requests
import json
from datetime import datetime
import aiosqlite
import aiohttp
from bot import DATABASE_NAME

FREE_GAMES_CACHE = {}


async def load_free_games_links(db):
    async with db.execute("SELECT * FROM free_games") as cursor:
        async for row in cursor:
            game_name = row[0]
            end_date = row[1]
            game_link = row[2]
            FREE_GAMES_CACHE[game_name] = {"end_date": end_date, "url": game_link}


async def get_free_games_links():
    # free_games = []
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
        # response = await requests.get(url)
        response_json = json.loads(raw_response)

        # Find all the games that are currently free
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

                end_date_str = end_date.strftime("%b %d, %Y")
                game_name = game["title"]
                game_link = f"https://launcher.store.epicgames.com/en-US/p/{slug}"

                FREE_GAMES_CACHE[game_name] = {
                    "end_date": end_date_str,
                    "url": game_link,
                }

            except Exception as e:
                print(
                    "features/epic_games: There is a broken Epic Games link: " + str(e)
                )

    except:
        print("features/epic_games: Failed to get free games list from Epic Games.")


async def send_free_games(client, chat_id):
    for game_name, game_data in FREE_GAMES_CACHE.items():
        end_date = game_data["end_date"]
        game_link = game_data["url"]

        message = f"{game_name} is free until {end_date}. Get it here: {game_link}"
        await client.send_message(chat_id, message)


async def insert_or_update_all_free_games(connection, cache):
    try:
        cursor = await connection.cursor()

        # Create a list of game_data dictionaries to insert/update
        game_data_list = [{"name": name, **data} for name, data in cache.items()]

        # Generate a single query to insert/update all games
        query = """
            INSERT OR REPLACE INTO free_games
            (name, end_date, url)
            VALUES (?, ?, ?)
            """

        # Execute the query with the list of game_data
        await cursor.executemany(
            query,
            [
                (
                    game["name"],
                    game["end_date"],
                    game["url"],
                )
                for game in game_data_list
            ],
        )

        # Now we will delete the games whose end_date has passed
        current_date = datetime.now().strftime("%b %d, %Y")
        delete_query = "DELETE FROM free_games WHERE end_date < ?"
        await cursor.execute(delete_query, (current_date,))

        # Commit the transaction
        await connection.commit()

        print("All free games data inserted/updated with a single query.")
    except aiosqlite.Error as e:
        # Rollback the transaction in case of an error
        await connection.rollback()
        print(f"Error inserting/updating free games data: {e}")
