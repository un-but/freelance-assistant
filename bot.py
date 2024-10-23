"""Main file launches bot via polling."""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from constants import TOKEN
from habr_scraper import get_data_from_habr
from kwork_scraper import get_data_from_kwork
from utils import add_user, get_users, remove_user

bot = Bot(token=TOKEN)
dp = Dispatcher()

# TODO попробоавать заменить time.sleep на asyncil.sleep
# TODO вынести работу с бд в отдельный файл db.py, а create_driver перенести в kwork_scraper
async def get_new_orders(*page_urls: str) -> list:
    """Distributes pages with orders between functions with logging of all actions.

    Supported sites:
        1. kwork.ru/projects
        2. freelance.habr.com/tasks

    Args:
        page_urls (list[str]): URL that can be processed by one of the functions

    Returns:
        set: contain tuples with information about each order

    """
    logging.info("Data collection started")
    new_orders = []

    for page_url in page_urls:
        if "https://freelance.habr.com/tasks" in page_url:
            new_orders.extend(await get_data_from_habr(page_url))
        elif "https://kwork.ru/projects" in page_url:
            new_orders.extend(await get_data_from_kwork(page_url))
        else:
            logging.info("%s URL is invalid")
            continue

        logging.info("Orders from the %s are collected", page_url)

    logging.info("Data collection ended")
    return new_orders


async def send_mailing() -> None:
    """Send new orders info to all users, runs every 3 minutes."""
    while True:
        await asyncio.sleep(5)
        new_orders = await get_new_orders(
            "https://freelance.habr.com/tasks?categories=development_bots",
            "https://kwork.ru/projects?c=41&attr=211",
            "https://kwork.ru/projects?c=41&attr=3587",
        )

        if new_orders:
            for new_order in new_orders:
                for user_id in await get_users():
                    order_text = (
                        f"<a href=\"{new_order[0]}\"><b>{new_order[1]}</b></a>\n"
                        f"<i>{new_order[4]}</i>\n"
                        f"<i>{new_order[2]}\t {new_order[5]}</i>\n\n"
                        f"{new_order[3]}"
                    )
                    await bot.send_message(chat_id=user_id, text=order_text, parse_mode="HTML")
            logging.info("Newsletter with new orders has been sent")
        else:
            logging.info("New orders not found")

        await asyncio.sleep(180)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    """Handle /start command, enables the user's mailing."""
    await add_user(message.from_user.username, message.from_user.id)

    await message.answer(
        "Здравствуйте, этот бот будет отправлять вам все новые заказы с сайтов https://freelance.habr.com/ и https://kwork.ru/."
        "Начиная пользоваться этим ботом вы запускаете рассылку."
        "Для отказа от использования бота используйте команду /stop - все ваши данные будут удалены, и вы не будете получать рассылку.",
    )


@dp.message(Command("stop"))
async def stop_handler(message: Message) -> None:
    """Handle /stop command, disables the user's mailing."""
    await remove_user(message.from_user.id)

    await message.answer(
        "Вы полностью отказались от рассылки. Спасибо что пользовались этим ботом!",
    )


async def main() -> None:
    """Launch a bot and a newsletter with the webhook disabled."""
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(
        asyncio.create_task(dp.start_polling(bot)),
        asyncio.create_task(send_mailing()),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(main())
