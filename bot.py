import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from constants import TOKEN
from habr_scraper import get_data_from_habr
from kwork_scraper import get_data_from_kwork
from utils import add_user, delete_user, get_all_users

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def send_mailing() -> None:
    while True:
        logging.info("сбор данных начался")
        new_habr_orders = await get_data_from_habr()
        logging.info("сбор с habr завершен")

        # FIXME result не равняется нулю при первом запуске
        new_kwork_orders = await get_data_from_kwork()
        logging.info("сбор с kwork завершен")

        new_orders = new_habr_orders.union(new_kwork_orders)

        print(new_orders)
        for user_id in await get_all_users():
            for order_text in new_orders:
                await bot.send_message(chat_id=user_id, text=order_text)
        logging.info("сбор данных закончился")
        await asyncio.sleep(180)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    await add_user(message)
    await message.answer(
        "Здравствуйте, этот бот будет отправлять вам все новые заказы с сайтов https://freelance.habr.com/ и https://kwork.ru/."
        "Начиная пользоваться этим ботом вы запускаете рассылку."
        "Для отказа от использования бота используйте команду /stop - все ваши данные будут удалены, и вы не будете получать рассылку.",
    )


@dp.message(Command("stop"))
async def stop_handler(message: Message) -> None:
    await delete_user(message)
    await message.answer(
        "Вы полностью отказались от рассылки. Спасибо что пользовались этим ботом!",
    )


async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(
        asyncio.create_task(dp.start_polling(bot)),
        asyncio.create_task(send_mailing()),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
