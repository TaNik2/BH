import asyncio

from aiogram import Bot, Dispatcher, executor
from config import BOT_TOCKEN

loop = asyncio.get_event_loop()
bot = Bot(token=BOT_TOCKEN, parse_mode="HTML")
dp = Dispatcher(bot, loop=loop)


if __name__ == "__main__":
    from kneco import dp, AlbumMiddleware
    dp.middleware.setup(AlbumMiddleware())
    executor.start_polling(dp, skip_updates=True)