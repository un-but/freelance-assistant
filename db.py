"""Functions for selenium and json with aiofiles."""

import aiosqlite


async def init_db() -> None:
    async with aiosqlite.connect("data.db") as db:
        await db.execute("""
                            CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY,
                                username TEXT,
                                user_id INTEGER UNIQUE NOT NULL
                            )
                         """)
        await db.execute("""
                            CREATE TABLE IF NOT EXISTS last_orders (
                                id INTEGER PRIMARY KEY,
                                page_url TEXT UNIQUE,
                                first_order TEXT,
                                second_order TEXT,
                                third_order TEXT
                            )
                         """)
        await db.commit()


async def add_last_orders(page_url: str, first_order: str, second_order: str, third_order: str) -> None:
    async with aiosqlite.connect("data.db") as db:
        await db.execute(
            """
                INSERT INTO last_orders (page_url, first_order, second_order, third_order)
                VALUES (?, ?, ?, ?)

                ON CONFLICT (page_url) DO UPDATE SET

                first_order=excluded.first_order,
                second_order=excluded.second_order,
                third_order=excluded.third_order
            """,
            (page_url, first_order, second_order, third_order),
        )
        await db.commit()


async def get_last_orders(page_url: str) -> list:
    async with aiosqlite.connect("data.db") as db:
        async with db.execute(
            "SELECT first_order, second_order, third_order FROM last_orders WHERE page_url = ?",
            (page_url,),
        ) as cur:
            last_orders = await cur.fetchone()
            return last_orders if last_orders else []


async def get_users() -> list:
    async with aiosqlite.connect("data.db") as db:
        async with db.execute("SELECT user_id FROM users") as cur:
            return [row[0] async for row in cur]


async def add_user(username: str, user_id: int) -> None:
    async with aiosqlite.connect("data.db") as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (username, user_id) VALUES (?, ?)",
            (username, user_id),
            )
        await db.commit()


async def remove_user(user_id: int) -> None:
    async with aiosqlite.connect("data.db") as db:
        await db.execute(
            "DELETE FROM users WHERE user_id = ?",
            (user_id,),
        )
        await db.commit()
