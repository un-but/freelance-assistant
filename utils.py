import json
from pathlib import Path

import aiofiles
from aiogram.types import Message
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options


def create_driver(mode: str = "headless") -> Chrome:
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
            "--start-maximized",
        ]
    elif mode == "desktop":
        # TODO Добавить функции для отображения браузера
        pass

    for option in options_list:
        options.add_argument(option)

    return Chrome(options=options)


async def create_basic_json() -> None:
    async with aiofiles.open("data.json", "w", encoding="utf-8") as file:
        await file.write(json.dumps({"users": [], "habr": [], "kwork": []}, indent=4, ensure_ascii=False))


async def json_load() -> dict:
    if not Path("data.json").exists():
        await create_basic_json()
    async with aiofiles.open("data.json", encoding="utf-8") as file:
        return json.loads(await file.read())


async def json_dump(array: dict) -> None:
    async with aiofiles.open("data.json", "w", encoding="utf-8") as file:
        await file.write(json.dumps(array, indent=4, ensure_ascii=False))


async def add_user(message: Message) -> None:
    json_file = await json_load()
    json_file["users"].append(message.from_user.id)
    await json_dump(json_file)


async def delete_user(message: Message) -> None:
    json_file = await json_load()
    json_file["users"].remove(message.from_user.id)
    await json_dump(json_file)


async def get_all_users() -> list:
    json_file = await json_load()
    return json_file["users"]
