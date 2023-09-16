import re
import asyncio
import aiosqlite
from bot import client, ADMIN_ID, DATABASE_NAME
from telethon.sync import events, types, Button
from data.admin_data import add_admin, delete_admin

setting_keyboard = [
    [Button.inline("🎖 مدیریت ادمین‌ها", "admin")],
]
setting_title = "👑 تنظیمات بات"


@client.on(events.NewMessage(pattern="(?i)/setting"))
async def handler(event):
    user = event.message.sender_id
    if user == ADMIN_ID:
        await client.send_message(
            event.chat_id, setting_title, buttons=setting_keyboard
        )
    else:
        sent_message = await client.send_message(
            event.chat_id, "⛔️ متاسفانه شما دسترسی لازم را ندارید ⛔️"
        )
        await asyncio.sleep(5)
        await client.delete_messages(event.chat_id, sent_message)


adminstrator_menu_keyboard = [
    [Button.inline("📝 لیست ادمین‌‌ها", "admins")],
    [Button.inline("➕ افزودن ادمین", "add_admin")],
]
adminstrator_menu_title = "🎖 تنظیمات ادمین‌ها"


@client.on(events.CallbackQuery(pattern=r"^admin$"))
async def callback(event):
    user = event._sender_id
    if user == ADMIN_ID:
        await client.edit_message(
            event.chat_id,
            event._message_id,
            adminstrator_menu_title,
            buttons=adminstrator_menu_keyboard,
        )
    else:
        await event.answer("You do not have permission")


@client.on(events.CallbackQuery(pattern=r"^add_admin$"))
async def callback(event):
    if event.sender_id == ADMIN_ID:
        await event.answer("افزودن ادمین جدید")
        # Start a new conversation
        async with client.conversation(event.chat_id) as conv:
            # Send a message to the user
            sent_message = await conv.send_message(
                "Please enter the admin username in the given format @username"
            )
            # Get the next message from the user
            response = await conv.get_response()
            if response.sender_id == ADMIN_ID:
                admin_name = response.raw_text
                # Check if the message is in the correct format
                if re.match(r"^@\w+$", admin_name):
                    try:
                        entity = await client.get_entity(admin_name)
                        if isinstance(entity, types.User):
                            await add_admin(conv, client, admin_name)
                            # await asyncio.sleep(4)
                            await client.delete_messages(event.chat_id, sent_message)
                            # Now you can do more stuff with the admin_name
                        else:
                            invalid_notification = await conv.send_message(
                                "Invalid username (not user)"
                            )
                            await asyncio.sleep(4)
                            await client.delete_messages(event.chat_id, sent_message)
                            await client.delete_messages(
                                event.chat_id, invalid_notification
                            )
                    except:
                        invalid_notification = await conv.send_message(
                            "Invalid user (user not found)"
                        )
                        await asyncio.sleep(4)
                        await client.delete_messages(event.chat_id, sent_message)
                        await client.delete_messages(
                            event.chat_id, invalid_notification
                        )
                    # Now you can do more stuff with the admin_name
                else:
                    invalid_notification = await conv.send_message("Invalid format")
                    await asyncio.sleep(4)
                    await client.delete_messages(event.chat_id, sent_message)
                    await client.delete_messages(event.chat_id, invalid_notification)
            else:
                await conv.send_message("You do not have permission to add a new admin")
    else:
        await event.answer("You do not have permission to add an admin")


admins_menu_title = "🎖 ادمین‌ها"


@client.on(events.CallbackQuery(pattern=r"^admins$"))
async def callback(event):
    user = event._sender_id
    if user == ADMIN_ID:
        connection = await aiosqlite.connect(DATABASE_NAME)
        cursor = await connection.cursor()
        await cursor.execute("SELECT * FROM admins")
        admins = await cursor.fetchall()
        await connection.close()
        global buttons
        buttons = []
        if admins:
            await event.answer("ادمین‌ها")
            for admin in admins:
                user_id, access_hash, date_added = admin
                user = await client.get_entity(types.PeerUser(user_id))
                if user.username:
                    buttons.append(
                        [
                            Button.inline(
                                f"@{user.username}", data=f"user:{user.username}"
                            )
                        ]
                    )
                else:
                    buttons.append(
                        [Button.inline(f"ID : {user_id}", data=f"user:{user_id}")]
                    )
            buttons.append([Button.inline("بازگشت", data="admin")])
            await client.edit_message(
                event.chat_id,
                event.message_id,
                adminstrator_menu_title,
                buttons=buttons,
            )
        else:
            await event.answer("ادمین وجود ندارد")
    else:
        await event.answer("You do not have permission")


admin_menu_title = "🛠 مدیریت ادمین"


@client.on(events.CallbackQuery(pattern=r"^user:(.*)$"))
async def handler(event):
    user_name = event.data_match.group(1).decode("utf-8")

    if event.sender_id == ADMIN_ID:
        print(user_name)
        admin_keyboard = (
            [
                Button.inline(f"{user_name} :حذف", data=f"delete:{user_name}"),
            ],
            [
                Button.inline(f"بازگشت", data="admins"),
            ],
        )
        await client.edit_message(
            event.chat_id, event._message_id, admin_menu_title, buttons=admin_keyboard
        )
    else:
        await event.answer("You do not have permission")
        await client.edit_message(event.chat_id, event._message_id, buttons=buttons)


@client.on(events.CallbackQuery(pattern=r"^delete:(.*)$"))
async def handler(event):
    user_id = event.data_match.group(1).decode("utf-8")

    if event.sender_id == ADMIN_ID:
        print(user_id)
        await delete_admin(event, client, user_id)
        await client.edit_message(
            event.chat_id,
            event.message_id,
            adminstrator_menu_title,
            buttons=adminstrator_menu_keyboard,
        )
    else:
        await event.answer("You do not have permission to delete an admin")