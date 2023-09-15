import aiosqlite

CHAT_DATA_CACHE = {}  # Dictionary to store chat data


async def load_chat_data(connection):
    cursor = await connection.cursor()
    await cursor.execute("SELECT * FROM chats")
    rows = await cursor.fetchall()
    for row in rows:
        chat_id = row[0]
        CHAT_DATA_CACHE[chat_id] = {
            "chat_id": chat_id,
            "access_hash": row[1],
            "title": row[2],
            # "type": row[3],
            "members_count": row[4],
            "last_interaction": row[5],
            "description": row[6],
            "link": row[7],
        }


async def update_chat_cache(chat_data):
    try:
        chat_id = chat_data["chat_id"]

        if chat_id in CHAT_DATA_CACHE:
            # Update the cache if chat data exists
            CHAT_DATA_CACHE[chat_id] = chat_data
            print("Chat data updated in cache.")
        else:
            # Insert new chat data into the cache
            CHAT_DATA_CACHE[chat_id] = chat_data
            print("Chat data inserted in cache.")

    except Exception as e:
        print(f"Error inserting/updating chat data in cache: {e}")


async def insert_or_update_all_chats(connection, cache):
    try:
        cursor = await connection.cursor()

        # Create a list of chat_data dictionaries to insert/update
        chat_data_list = list(cache.values())

        # Generate a single query to insert/update all chats
        query = """
            INSERT OR REPLACE INTO chats
            (chat_id, access_hash, title, members_count,
            last_interaction, description, link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """

        # Execute the query with the list of chat_data
        await cursor.executemany(
            query,
            [
                (
                    chat["chat_id"],
                    chat["access_hash"],
                    chat["title"],
                    chat["members_count"],
                    chat["last_interaction"],
                    chat["description"],
                    chat["link"],
                )
                for chat in chat_data_list
            ],
        )

        # Commit the transaction
        await connection.commit()

        print("All chat data inserted/updated with a single query.")
    except aiosqlite.Error as e:
        # Rollback the transaction in case of an error
        await connection.rollback()
        print(f"Error inserting/updating chat data: {e}")
