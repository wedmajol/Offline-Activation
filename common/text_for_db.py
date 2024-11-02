from aiogram.utils.formatting import Bold, as_marked_section
description_for_info_pages = {
    "main": "Добро пожаловать!",
    "about": "Вас приветствует магазин ...\nАвтовыдача после оплаты",
    "catalog": "Список всех аккаунтов",
    "searchgame": "Игры",
    "payment": as_marked_section(
        Bold("Варианты оплаты:"),
        "Картой в боте",
        "При получении карта/кеш",
        "В заведении",
        marker="✅ ",
    ).as_markdown(),
}