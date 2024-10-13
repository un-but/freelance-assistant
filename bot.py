import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from constants import TOKEN
from db import add_user, delete_user, get_all_users
from habr_scraper import get_data_from_habr
from kwork_scraper import get_data_from_kwork

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def send_mailing() -> None:
    while True:
        # TODO Правильно поделить функции на сохранение в бд и возврат самого заказа для отправки
        orders = {await get_data_from_habr()} | {get_data_from_kwork()}
        for user_id in await get_all_users():
            for order_text in orders:
                bot.send_message(chat_id=user_id, text=order_text)
        asyncio.sleep(180)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    await add_user(message)
    await message.answer(
        "Здравствуйте, этот бот будет отправлять вам все новые заказы с сайтов https://freelance.habr.com/ и https://kwork.ru/."
        "Начиная пользоваться этим ботом вы запускаете рассылку."
        "Для отказа от использования бота используйте команду /stop - все ваши данные будут удалены, и вы не будете получать рассылку."
    )


@dp.message(Command("stop"))
async def stop_handler(message: Message) -> None:
    await delete_user(message)
    await message.answer(
        "Вы полностью отказались от рассылки. Спасибо что пользовались этим ботом!"
    )


async def main() -> None:
    asyncio.get_event_loop().create_task(send_mailing())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
