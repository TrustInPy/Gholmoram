import aiosqlite
import asyncio
from bot import DATABASE_NAME
from data.chats_data import load_chat_data
from .epic_game_data import load_free_games_links

USER_DATA_CACHE = {}  # Dictionary to store user data


async def create_database(DATABASE_NAME):
    try:
        connection = await aiosqlite.connect(DATABASE_NAME)
        print("Database connection established.")
        return connection
    except aiosqlite.Error as e:
        print(f"Error: {e}")
        return None


async def create_users_table(connection):
    try:
        cursor = await connection.cursor()
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER NOT NULL UNIQUE PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_interaction TIMESTAMP,
                access_hash INTEGER,
                bio TEXT,
                is_bot INTEGER
            )
        """
        )
        await connection.commit()
        print("Users table created.")
    except aiosqlite.Error as e:
        print(f"Error creating table: {e}")


async def create_chats_table(connection):
    try:
        cursor = await connection.cursor()
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER NOT NULL UNIQUE PRIMARY KEY,
                access_hash INTEGER,
                title TEXT,
                type TEXT,
                members_count INTEGER,
                last_interaction TIMESTAMP,
                description TEXT,
                link TEXT
            )
        """
        )
        await connection.commit()
        print("Chats table created.")
    except aiosqlite.Error as e:
        print(f"Error creating table: {e}")


async def create_messages_table(connection):
    try:
        cursor = await connection.cursor()
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                chat_id INTEGER,
                user_id INTEGER,
                message_id INTEGER,
                message_text TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reply_to_message_id INTEGER,
                forward_from_user_id INTEGER,
                PRIMARY KEY (chat_id, message_id),
                FOREIGN KEY (chat_id) REFERENCES chats(chat_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (reply_to_message_id) REFERENCES messages(message_id),
                FOREIGN KEY (forward_from_user_id) REFERENCES users(user_id)
            )
        """
        )
        await connection.commit()
        print("Messages table created.")
    except aiosqlite.Error as e:
        print(f"Error creating table: {e}")


async def create_admins_table(connection):
    try:
        cursor = await connection.cursor()
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER,
                access_hash INTEGER,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """
        )
        await connection.commit()
        print("Admins table created.")
    except aiosqlite.Error as e:
        print(f"Error creating table: {e}")


async def create_epic_game_table(connection):
    try:
        cursor = await connection.cursor()
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS free_games (
                name TEXT NOT NULL PRIMARY KEY,
                end_date TEXT NOT NULL,
                url TEXT NOT NULL
            );

            """
        )
        await connection.commit()
        print("Epic game table created.")
    except aiosqlite.Error as e:
        print(f"Error creating table: {e}")


async def load_user_data(connection):
    cursor = await connection.cursor()
    await cursor.execute("SELECT * FROM users")
    rows = await cursor.fetchall()
    for row in rows:
        user_id = row[0]
        USER_DATA_CACHE[user_id] = {
            "user_id": user_id,
            "username": row[1],
            "first_name": row[2],
            "last_name": row[3],
            "date_joined": row[4],
            "last_interaction": row[5],
            "access_hash": row[6],
            "bio": row[7],
            "is_bot": row[8],
        }


async def insert_or_update_all_users(connection, cache):
    try:
        cursor = await connection.cursor()

        # Create a list of user_data dictionaries to insert/update
        user_data_list = list(cache.values())

        # Generate a single query to insert/update all users
        query = """
            INSERT OR REPLACE INTO users
            (user_id, username, first_name, last_name, date_joined,
            last_interaction, access_hash, bio, is_bot)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

        # Execute the query with the list of user_data
        await cursor.executemany(
            query,
            [
                (
                    user["user_id"],
                    user["username"],
                    user["first_name"],
                    user["last_name"],
                    user["date_joined"],
                    user["last_interaction"],
                    user["access_hash"],
                    user["bio"],
                    user["is_bot"],
                )
                for user in user_data_list
            ],
        )

        # Commit the transaction
        await connection.commit()

        print("All user data inserted/updated with a single query.")
    except aiosqlite.Error as e:
        # Rollback the transaction in case of an error
        await connection.rollback()
        print(f"Error inserting/updating user data: {e}")


async def update_cache(user_data):
    try:
        user_id = user_data["user_id"]

        if user_id in USER_DATA_CACHE:
            # Update the cache if user data exists
            existing_data = USER_DATA_CACHE[user_id]
            # Preserve the original date_joined value
            user_data["date_joined"] = existing_data["date_joined"]
            USER_DATA_CACHE[user_id] = user_data
            print("User data updated in cache.")
        else:
            # Insert new user data into the cache
            USER_DATA_CACHE[user_id] = user_data
            print("User data inserted in cache.")

    except Exception as e:
        print(f"Error inserting/updating user data in cache: {e}")


async def run_database():
    conn = await create_database(DATABASE_NAME)
    await create_users_table(conn)
    await create_chats_table(conn)
    await create_messages_table(conn)
    await create_admins_table(conn)
    await create_epic_game_table(conn)
    await load_user_data(conn)
    await load_chat_data(conn)
    await load_free_games_links(conn)
    await conn.close()


if __name__ == "__main__":
    asyncio.run(run_database())
