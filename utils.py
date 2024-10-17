"""Functions for selenium and json with aiofiles."""

import json
from pathlib import Path

import aiofiles
from aiogram.types import Message
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options


def create_driver(mode: str = "desktop") -> Chrome:
    """Create chrome driver object.

    Args:
        mode (str, optional): "headless" for server and "desktop" or not specify for debug with graphical interface
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
        ]
    elif mode == "desktop":
        options_list = [
            "--ignore-certificate-errors-spki-list",
            "--log-level=3",
        ]


    for option in options_list:
        options.add_argument(option)

    return Chrome(options=options)


async def json_load() -> dict:
    """Return json file, if file doesn't exists, create its basic version and return it."""
    if not Path("data.json").exists():
        basic_json = {"users": [], "habr": [], "kwork": []}
        await json_dump(basic_json)
    async with aiofiles.open("data.json", encoding="utf-8") as file:
        return json.loads(await file.read())


async def json_dump(json_object: dict) -> None:
    """Dump dictionary to json file."""
    async with aiofiles.open("data.json", "w", encoding="utf-8") as file:
        await file.write(json.dumps(json_object, indent=4, ensure_ascii=False))
