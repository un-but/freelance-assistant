import aiosqlite
from aiogram.types import Message

async def init_db() -> None:
    async with aiosqlite.connect("users_data.db") as db:
        await db.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT,
                        user_id INTEGER NOT NULL,
                        )
                    """)
        await db.execute("""
                    CREATE TABLE IF NOT EXISTS  (
                        id INTEGER PRIMARY KEY,
                        message_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        message_time INTEGER NOT NULL
                    )
                    """)
        await db.execute("""
                    CREATE TABLE IF NOT EXISTS globals (
                        id INTEGER PRIMARY KEY,
                        prohibit_sending_time INTEGER,
                        bot_id INTEGER,
                        bot_name TEXT,
                        bot_username TEXT
                    )
                    """)
        await db.commit()

    
async def add_user(message: Message) -> None:
    async with aiosqlite.connect("users_data.db") as db:
        await db.execute(
            "INSERT INTO users username, user_id VALUES (?, ?)",
            (message.from_user.username, message.from_user.id)
        )


async def delete_user(message: Message) -> None:
    async with aiosqlite.connect("users_data.db") as db:
        await db.execute(
            "DELETE FROM users WHERE user_id = ?",
            (message.from_user.id,)
        )


async def get_all_users() -> list:
    pass


async def add_order_to_db(order_url, order_name, order_date, order_description, order_price, order_responses):
    pass


async def check_new_orders():
    pass