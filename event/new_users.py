# import sqlite3
# from bot import client
# from telethon.sync import events
# import datetime
# from telethon.tl.functions.users import GetFullUserRequest


# user_id_cache = {}


# def load_user_ids(connection):
#     cursor = connection.cursor()
#     cursor.execute("SELECT user_id FROM users")
#     rows = cursor.fetchall()
#     for row in rows:
#         user_id_cache[row[0]] = True


# conn = sqlite3.connect("GholDB.db")
# load_user_ids(conn)
# conn.close()


# def insert_user(connection, user_data):
#     try:
#         cursor = connection.cursor()

#         # cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_data[0],))
#         # if cursor.fetchone()[0] > 0:
#         #     print("User already exists.")
#         #     return

#         if user_data[0] in user_id_cache:
#             print("User already exists.")
#             return

#         cursor.execute(
#             """
#             INSERT INTO users (user_id, username, first_name, last_name, date_joined,
#                                last_interaction, access_hash, bio, is_bot)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#         """,
#             user_data,
#         )
#         connection.commit()

#         user_id_cache[user_data[0]] = True

#         print("User data inserted.")
#     except sqlite3.Error as e:
#         print(f"Error inserting user data: {e}")


# @client.on(events.NewMessage(func=lambda e: e.is_private))
# async def handler(event):
#     a = []
#     user_id = event.chat_id
#     a.append(user_id)
#     username = event.chat.username
#     a.append(username)
#     first_name = event.chat.first_name
#     a.append(first_name)
#     last_name = event.chat.last_name
#     a.append(last_name)
#     date_joined = datetime.datetime.now()
#     a.append(date_joined)
#     last_interaction = datetime.datetime.now()
#     a.append(last_interaction)
#     access_hash = event.chat.access_hash
#     a.append(access_hash)
#     full = await client(GetFullUserRequest(user_id))
#     bio = full.full_user.about
#     a.append(bio)
#     is_bot = event.chat.bot
#     a.append(is_bot)

#     print(bio)


#     if user_id not in user_id_cache:
#         conn = sqlite3.connect("GholDB.db")
#         insert_user(conn, a)
#         conn.close()

#     print("Done")

