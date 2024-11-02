import asyncio
import os
import locale

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from db.engine import create_db, drop_db, session_maker
from midleware.db import DataBaseSession

from handlers.admin import admin_router
from handlers.user import user_router
from common.bot_cmds_list import private_client, private_admin

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

bot = Bot(token=os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
bot.my_admins_list = ["ardyn_lucis"]

dp = Dispatcher()

dp.include_routers(admin_router, user_router)

async def on_startup():

    await drop_db()

    await create_db()


async def on_shutdown():
    print ('Бот лег')

async def set_admin_coomands(username: str):
    admin_id = await bot.get_chat(username)
    if admin_id:
        await bot.set_my_commands(commands=private_admin, scope = types.BotCommandScopeChat(chat_id=admin_id))

async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private_client, scope=types.BotCommandScopeAllPrivateChats())
    for admin_username in bot.my_admins_list:
        await set_admin_coomands(admin_username)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

asyncio.run(main())
