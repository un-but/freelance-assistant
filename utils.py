"""Functions for selenium and json with aiofiles."""

import json
from pathlib import Path

import aiofiles
from aiogram.types import Message
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options


def create_driver(mode: str = "headless") -> Chrome:
    """Create chrome driver object.

    Args:
        mode (str, optional): "headless" for server or "desktop" for debug. Defaults to "headless"

    Returns:
        Chrome: chrome driver object

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
            "--start-maximized",
        ]
    elif mode == "desktop":
        # TODO Добавить функции для отображения браузера
        pass

    for option in options_list:
        options.add_argument(option)

    return Chrome(options=options)


async def create_basic_json() -> None:
    """Create json file with users, habr and kwork lists."""
    async with aiofiles.open("data.json", "w", encoding="utf-8") as file:
        await file.write(json.dumps({"users": [], "habr": [], "kwork": []}, indent=4, ensure_ascii=False))


async def json_load() -> dict:
    """Return json file, if file doesn't exists, create its base version and return it."""
    if not Path("data.json").exists():
        await create_basic_json()
    async with aiofiles.open("data.json", encoding="utf-8") as file:
        return json.loads(await file.read())


async def json_dump(array: dict) -> None:
    """Dump dictionary to json file."""
    async with aiofiles.open("data.json", "w", encoding="utf-8") as file:
        await file.write(json.dumps(array, indent=4, ensure_ascii=False))


async def add_user(message: Message) -> None:
    """Add user to users list by id from message."""
    json_file = await json_load()
    json_file["users"].append(message.from_user.id)
    await json_dump(json_file)


async def delete_user(message: Message) -> None:
    """Delete user from users list."""
    json_file = await json_load()
    json_file["users"].remove(message.from_user.id)
    await json_dump(json_file)


async def get_all_users() -> list:
    """Return users list."""
    json_file = await json_load()
    return json_file["users"]
