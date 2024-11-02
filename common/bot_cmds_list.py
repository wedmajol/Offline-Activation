from aiogram.types import BotCommand

#Добавить команды отдельно для админа и клиента

private_client = [
    BotCommand(command='main', description='Главное меню'),
    BotCommand(command='about', description='О нас'),
    BotCommand(command='payment', description='Варианты оплаты'),
    BotCommand(command='shipping', description='Варианты доставки')
]

private_admin = [
    BotCommand(command='admin', description= 'Меню администратора'),
    BotCommand(command='main', description='Главное меню'),
    BotCommand(command='about', description='О нас'),
    BotCommand(command='payment', description='Варианты оплаты'),
    BotCommand(command='shipping', description='Варианты доставки')
]