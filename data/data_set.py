import sqlite3
# from bot import DATABASE_NAME

DATABASE_NAME = "GholDB.db"


def create_database(DATABASE_NAME):
    try:
        connection = sqlite3.connect(DATABASE_NAME)
        print("Database connection established.")
        return connection
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return None


def create_users_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER NOT NULL UNIQUE PRIMARY KEY,
                username TEXT ,
                first_name TEXT,
                last_name TEXT,
                date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_interaction TIMESTAMP,
                access_hash INTEGER,
                bio TEXT,
                is_bot INTEGER,
                last_update_time TIMESTAMP
            )
        ''')
        connection.commit()
        print("Users table created.")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")




def create_chats_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute('''
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
        ''')
        connection.commit()
        print("Chats table created.")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")






def create_messages_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute('''
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
        ''')
        connection.commit()
        print("Messages table created.")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")










conn = create_database(DATABASE_NAME)
create_users_table(conn)
create_chats_table(conn)
create_messages_table(conn)


