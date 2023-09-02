import sqlite3
from bot import client
from telethon.sync import events
import datetime
from telethon.tl.functions.users import GetFullUserRequest

# Define the update duration time in seconds (10 hours by default)
UPDATE_DURATION_SECONDS = 10#10 * 3600

user_data_cache = {}  # Dictionary to store user data

def load_user_data(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        user_id = row[0]
        user_data_cache[user_id] = {
            "user_id": user_id,
            "username": row[1],
            "first_name": row[2],
            "last_name": row[3],
            "date_joined": row[4],
            "last_interaction": row[5],
            "access_hash": row[6],
            "bio": row[7],
            "is_bot": row[8],
            "last_update_time": row[9]  # Add a new column for last update time
        }



def insert_or_update_user(connection, user_data):
    try:
        cursor = connection.cursor()
        user_id = user_data["user_id"]

        if user_id in user_data_cache:
            last_update_time = user_data_cache[user_id]["last_update_time"]
            current_time = int(datetime.datetime.now().timestamp())

            # Check if it's been at least the specified update duration since the last update
            if (current_time - last_update_time) < UPDATE_DURATION_SECONDS:
                print("User data is up to date. Skipping update.")
                return

            # Update user data if it's time for an update
            cursor.execute(
                """
                UPDATE users SET
                username = ?,
                first_name = ?,
                last_name = ?,
                date_joined = ?,
                last_interaction = ?,
                access_hash = ?,
                bio = ?,
                is_bot = ?,
                last_update_time = ?
                WHERE user_id = ?
                """,
                (
                    user_data["username"],
                    user_data["first_name"],
                    user_data["last_name"],
                    user_data["date_joined"],
                    user_data["last_interaction"],
                    user_data["access_hash"],
                    user_data["bio"],
                    user_data["is_bot"],
                    current_time,  # Update the last update time
                    user_id
                )
            )
        else:
            # Insert new user data if it doesn't exist
            cursor.execute(
                """
                INSERT INTO users (user_id, username, first_name, last_name, date_joined,
                                   last_interaction, access_hash, bio, is_bot, last_update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_data["user_id"],
                    user_data["username"],
                    user_data["first_name"],
                    user_data["last_name"],
                    user_data["date_joined"],
                    user_data["last_interaction"],
                    user_data["access_hash"],
                    user_data["bio"],
                    user_data["is_bot"],
                    int(datetime.datetime.now().timestamp())  # Set the initial last update time
                )
            )

        connection.commit()
        user_data_cache[user_id] = user_data  # Update the cache

        print("User data inserted/updated.")
    except sqlite3.Error as e:
        print(f"Error inserting/updating user data: {e}")

@client.on(events.NewMessage(func=lambda e: e.is_private))
async def handler(event):
    conn = sqlite3.connect("GholDB.db")
    load_user_data(conn)
    conn.close()

    user_id = event.chat_id
    username = event.chat.username
    first_name = event.chat.first_name
    last_name = event.chat.last_name
    date_joined = datetime.datetime.now()
    last_interaction = datetime.datetime.now()
    access_hash = event.chat.access_hash
    full = await client(GetFullUserRequest(user_id))
    bio = full.full_user.about
    is_bot = event.chat.bot

    user_data = {
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "date_joined": date_joined,
        "last_interaction": last_interaction,
        "access_hash": access_hash,
        "bio": bio,
        "is_bot": is_bot
    }

    conn = sqlite3.connect("GholDB.db")
    insert_or_update_user(conn, user_data)
    conn.close()

    print("Done")
