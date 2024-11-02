from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class Menucallback(CallbackData, prefix ="menu"):
    level: int
    menu_name: str
    page: int = 1

class BUYcallback(CallbackData, prefix = 'cart'):
    menu_name: str


##################Создание инлайн клавиатуры  ################################################################
def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():

        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


def get_user_main_btns(*, level:int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Аккаунты": "catalog",
        "О нас ": "about",
        "Оплата": "payment",
        }
    for text, menu_name  in btns.items():
        if menu_name == 'catalog':
            keyboard.add(InlineKeyboardButton(text=text, callback_data=Menucallback(level=1, menu_name=menu_name).pack()))
        elif menu_name == 'cart':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=Menucallback(level=3, menu_name=menu_name).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=Menucallback(level=level, menu_name=menu_name).pack()))

    return keyboard.adjust(*sizes).as_markup()


############################################################Клавиатура возвращения на перыдущий лвл############################################################
def back_kbds(
    *,
    level: int,
    sizes: tuple[int] = (2, 1)
):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Назад',
                callback_data=Menucallback(level=level -1, menu_name='catalog').pack()))

    keyboard.adjust(*sizes)
    return keyboard.as_markup()


############################################################Клавиатура покупки############################################################
def buying_kbds(
    *,
    game_id: int,
    sizes: tuple[int] = (2, 1)
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Купить 💵',
                callback_data=BUYcallback(menu_name='add_to_cart', game_id=game_id).pack()))

    keyboard.adjust(*sizes)


    return keyboard.as_markup()
