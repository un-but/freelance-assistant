import json
import os

import aiofiles
from aiogram.types import Message
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

# async def init_db() -> None:
#     async with aiosqlite.connect("users_data.db") as db:
#         await db.execute("""
#                     CREATE TABLE IF NOT EXISTS users (
#                         id INTEGER PRIMARY KEY,
#                         username TEXT,
#                         user_id INTEGER NOT NULL,
#                         )
#                     """)
#         await db.execute("""
#                     CREATE TABLE IF NOT EXISTS  (
#                         id INTEGER PRIMARY KEY,
#                         message_id INTEGER NOT NULL,
#                         user_id INTEGER NOT NULL,
#                         message_time INTEGER NOT NULL
#                     )
#                     """)
#         await db.execute("""
#                     CREATE TABLE IF NOT EXISTS globals (
#                         id INTEGER PRIMARY KEY,
#                         prohibit_sending_time INTEGER,
#                         bot_id INTEGER,
#                         bot_name TEXT,
#                         bot_username TEXT
#                     )
#                     """)
#         await db.commit()


# async def add_user(message: Message) -> None:
#     async with aiosqlite.connect("users_data.db") as db:
#         await db.execute(
#             "INSERT INTO users username, user_id VALUES (?, ?)",
#             (message.from_user.username, message.from_user.id)
#         )


# async def delete_user(message: Message) -> None:
#     async with aiosqlite.connect("users_data.db") as db:
#         await db.execute(
#             "DELETE FROM users WHERE user_id = ?",
#             (message.from_user.id,)
#         )


# async def get_all_users() -> list:
#     pass


# async def add_order_to_db(order_url, order_name, order_date, order_description, order_price, order_responses):
#     pass


# async def check_new_orders():
#     pass


def create_driver(mode="headless") -> Chrome:
    """Create chrome driver object.

    Args:
        mode (str, optional): "headless" for server or "desktop" for debug. Defaults to "headless".

    Returns:
        webdriver.Chrome
    """
    options = Options()

    if mode == "headless":
        options_list = [
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--headless",
            "--ignore-certificate-errors-spki-list",
            "--log-level=3",
            "--start-maximized"
        ]
    elif mode == "desktop":
        # Добавить функции для отображения браузера
        pass

    for option in options_list:
        options.add_argument(option)

    return Chrome(options=options)


async def create_basic_json() -> None:
    async with aiofiles.open("data.json", "w", encoding="utf-8") as file:
        await file.write(json.dumps({"users": [], "habr": [], "kwork": []}, indent=4, ensure_ascii=False))


async def json_load() -> list:
    if not os.path.exists("data.json"):
        await create_basic_json()
    async with aiofiles.open("data.json", encoding="utf-8") as file:
        return json.loads(await file.read())


async def json_dump(array: list) -> None:
    async with aiofiles.open("data.json", "w", encoding="utf-8") as file:
        await file.write(json.dumps(array, indent=4, ensure_ascii=False))


async def add_user(message: Message) -> None:
    pass


async def get_all_users() -> list:
    pass


async def delete_user(message: Message) -> None:
    pass
