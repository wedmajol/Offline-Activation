from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram import F
from sqlalchemy.ext.asyncio import AsyncSession
from db.orm_query import orm_get_accounts_by_game
from kbds.inline import Menucallback, buying_kbds
from handlers.menu_proccesing import game_catalog, get_menu_content

user_router = Router()

@user_router.message(CommandStart())
async def main_menu(message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)

@user_router.callback_query(Menucallback.filter())
async def user_menu(callback: types.CallbackQuery, callback_data: Menucallback, session: AsyncSession):

    result = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name
    )
    if result is None:
        await callback.answer("Не удалось получить данные.", show_alert=True)
        return
    media, reply_markup = result
    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


@user_router.callback_query(F.data.startswith('category_'))
async def process_show_game(callback: types.CallbackQuery, session: AsyncSession):
    # Извлекаем категорию из колбек-данных
    game_cat = callback.data.split('_')[-1]  # Получаем название категории
    message_text, kbds = await game_catalog(session, game_cat, level=2)
    # Отправляем сообщение пользователю
    await callback.message.edit_media(message_text, reply_markup=kbds)
    await callback.answer()



@user_router.message()
async def game_search(message: types.Message, session: AsyncSession):
    game = message.text
    games = await orm_get_accounts_by_game(session, game)
    games_list = [account.gamesonaacaunt for account in games]
    if game not in games_list or not F.text:
        await message.answer('Напиши старт')
        return

    for game in games:  # Проходим по всем найденным услугам
        account_info = (
            f"{game.description}\n"
            f"Игра: {game.gamesonaacaunt}\n"  # Используем service
            f"Цена: {game.price} rub"
        )

        kbds = buying_kbds(
            game_id=game.id  # Используем service вместо services
        )
        await message.answer_photo(photo=game.image,caption=account_info, reply_markup=kbds)
