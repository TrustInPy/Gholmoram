import asyncio
import aiosqlite
from bot import DATABASE_NAME


async def add_admin(conv, client, username):
    try:
        try:
            user = await client.get_entity(username)
        except Exception as e:
            print(e)
            sent_message = await conv.send_message(f"User {username} not found.")
            await asyncio.sleep(4)
            await client.delete_messages(conv.chat_id, sent_message)
            return
        connection = await aiosqlite.connect(DATABASE_NAME)
        cursor = await connection.cursor()
        user_id, access_hash = user.id, user.access_hash

        # Check if admin already exists
        await cursor.execute(
            """
            SELECT * FROM admins WHERE user_id = ?
            """,
            (user_id,),
        )
        data = await cursor.fetchone()
        if data is not None:
            sent_message = await conv.send_message(f"Admin {username} already exists.")
            await asyncio.sleep(4)
            await client.delete_messages(conv.chat_id, sent_message)
            return

        # Insert into admins table
        await cursor.execute(
            """
            INSERT INTO admins (user_id, access_hash) VALUES (?, ?)
            """,
            (user_id, access_hash),
        )
        await connection.commit()
        sent_message = await conv.send_message(f"Admin {username} added.")
        await asyncio.sleep(4)
        await client.delete_messages(conv.chat_id, sent_message)
    except aiosqlite.Error as e:
        print(f"Error adding admin: {e}")
        sent_message = await conv.send_message("Error adding admin")
        await asyncio.sleep(4)
        await client.delete_messages(conv.chat_id, sent_message)
    finally:
        await connection.close()


async def delete_admin(event, client, user_identifier):
    try:
        try:
            if user_identifier.isdigit():
                user_identifier = int(user_identifier)
            if isinstance(user_identifier, int):
                user = await client.get_entity(user_identifier)
            else:
                user = await client.get_entity(user_identifier)
        except Exception as e:
            print(e)
            sent_message = await event.respond(f"User {user_identifier} not found.")
            await asyncio.sleep(4)
            await client.delete_messages(event.chat_id, sent_message)
            return

        connection = await aiosqlite.connect(DATABASE_NAME)
        cursor = await connection.cursor()
        user_id = user.id

        # Check if admin exists
        await cursor.execute(
            """
            SELECT * FROM admins WHERE user_id = ?
            """,
            (user_id,),
        )
        data = await cursor.fetchone()
        if data is None:
            sent_message = await event.respond(
                f"Admin {user_identifier} does not exist."
            )
            await asyncio.sleep(4)
            await client.delete_messages(event.chat_id, sent_message)
            return

        # Delete from admins table
        await cursor.execute(
            """
            DELETE FROM admins WHERE user_id = ?
            """,
            (user_id,),
        )
        await connection.commit()
        sent_message = await event.respond(f"Admin {user_identifier} deleted.")
        await asyncio.sleep(4)
        await client.delete_messages(event.chat_id, sent_message)
    except aiosqlite.Error as e:
        print(f"Error deleting admin: {e}")
        sent_message = await event.respond(f"Error deleting admin")
        await asyncio.sleep(4)
        await client.delete_messages(event.chat_id, sent_message)
    finally:
        await connection.close()
