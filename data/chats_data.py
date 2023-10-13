async def load_chat_data(connection, chat_id):
    cursor = await connection.cursor()
    await cursor.execute("SELECT * FROM chats WHERE chat_id = ?", (chat_id,))
    row = await cursor.fetchone()
    if row is not None:
        return {
            "chat_id": row[0],
            "access_hash": row[1],
            "title": row[2],
            "members_count": row[3],
            "last_interaction": row[4],
            "description": row[5],
            "link": row[6],
            "epic_notification": row[7],
        }
    else:
        return None


async def update_chat_cache(connection, chat_data):
    cursor = await connection.cursor()
    query = """
        INSERT OR REPLACE INTO chats
        (chat_id, access_hash, title, members_count,
        last_interaction, description, link, epic_notification)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
    await cursor.execute(
        query,
        (
            chat_data["chat_id"],
            chat_data["access_hash"],
            chat_data["title"],
            chat_data["members_count"],
            chat_data["last_interaction"],
            chat_data["description"],
            chat_data["link"],
            chat_data.get("epic_notification", None),
        ),
    )
    await connection.commit()
