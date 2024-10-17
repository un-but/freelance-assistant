"""Main file launches bot via polling."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from constants import TOKEN
from habr_scraper import get_data_from_habr
from kwork_scraper import get_data_from_kwork
from utils import json_dump, json_load

bot = Bot(token=TOKEN)
dp = Dispatcher()

# TODO добавить функцию, которая будет автоматически распределять заказы по функциям в зависимости от домена
# TODO проверить работу, если последний заказ так и не был найден (на другой странице)

async def send_mailing() -> None:
    """Send new orders info to all users, runs every 3 minutes."""
    while True:
        logging.info("Data collection started")
        new_habr_orders = await get_data_from_habr()
        logging.info("Habr data collection ended")

        new_kwork_orders = await get_data_from_kwork()
        logging.info("Kwork data collection ended")

        new_orders = new_habr_orders.union(new_kwork_orders)
        logging.info("Data collection ended")

        for user_id in (await json_load())["users"]:
            for new_order in new_orders:
                order_text = (
                    f"<a href=\"{new_order[0]}\"><b>{new_order[1]}</b></a>\n"
                    f"<i>{new_order[4]}</i>\n"
                    f"<i>{new_order[2]}\t {new_order[5]}</i>\n\n"
                    f"{new_order[3]}"
                )
                await bot.send_message(chat_id=user_id, text=order_text, parse_mode="HTML")
        logging.info("Newsletter with new orders has been sent")
        await asyncio.sleep(180)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    """Handle /start command, enables the user's mailing."""
    json_file = await json_load()
    json_file["users"].append(message.from_user.id)
    await json_dump(json_file)

    await message.answer(
        "Здравствуйте, этот бот будет отправлять вам все новые заказы с сайтов https://freelance.habr.com/ и https://kwork.ru/."
        "Начиная пользоваться этим ботом вы запускаете рассылку."
        "Для отказа от использования бота используйте команду /stop - все ваши данные будут удалены, и вы не будете получать рассылку.",
    )


@dp.message(Command("stop"))
async def stop_handler(message: Message) -> None:
    """Handle /stop command, disables the user's mailing."""
    json_file = await json_load()
    json_file["users"].remove(message.from_user.id)
    await json_dump(json_file)

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
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
