from aiogram import types, Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db.orm_query import (
    orm_add_admin,
    orm_add_game,
    orm_delete_admin,
    orm_delete_game,
    orm_get_admin,
    orm_get_admins,
    orm_get_game,
    orm_get_games,
    orm_get_info_pages,
    orm_change_banner_image,
    orm_update_catalog,
)
from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.inline import get_callback_btns

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


####################################АВТОДОБАВЛЕНИЕ АДМИНА ИЗ ЛИСТА ADMINLIST####################################
@admin_router.message(Command('main_admin'))
async def add_admin(message: types.Message, bot: Bot, session: AsyncSession):
    if message.from_user.username in bot.my_admins_list:
        main_admin = await orm_get_admin(session, message.from_user.username)

        if main_admin is None:
            # Если пользователя нет в базе, добавляем его
            await orm_add_admin(session, message.from_user.username)
            await message.answer('Теперь вы главный администратор')
        else:
            await message.answer(
                'Вы уже главный администратор '
        )
    else:
        await message.reply(
            'Вы не можете получить права главого администратора'
        )

#################################### Главное меню администратора ####################################

@admin_router.callback_query(F.data==('admin'))
@admin_router.message(Command('admin'))
async def admin_commands_cb(callback: types.CallbackQuery, message: types.Message):
    await callback.message.answer(
        'Нажмите на интересующую вас команду', reply_markup=get_callback_btns(btns={
            'Менеджемнт игр': 'game_manage',
            'Добавить изменить банер':  'banner'
        },
        sizes=(1,1,))
    )
    await callback.message.delete()

################################### Менеджмента администраторов ####################################

@admin_router.callback_query(Command("admin_manage"))
async def comm_adm(callback: types.CallbackQuery, bot: Bot):
    if callback.from_user.id in bot.my_admins_list:
        await callback.message.answer(
            'Что хочешь??',reply_markup=get_callback_btns(btns={
                'Добавить админа': 'add_admin',
                'Удалить админа': 'delete_admin',
                'Назад': 'admin'
            }, sizes=(2,1))
        )
    else:
        await callback.message.answer("У вас нет доступа к этим командам")

#################################### Менеджмент аккаунтов с играми ####################################

@admin_router.callback_query(F.data == ('game_manage'))
async def account_manage(callback: types.CallbackQuery,):
    await callback.message.answer(
        'Что вы хотите сделать?',reply_markup=get_callback_btns(btns={
            'Добавить игру': 'add_game',
            'Изменить аккаунты': 'show_games',
            'Назад': 'admin'
        },sizes=(2,))
        )

#################################### Добавление администратора ####################################
class AddAdmin(StatesGroup):
    username = State()

@admin_router.callback_query(F.data == ('add_admin'))
async def add_new_admin(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите тг-логин добавляемого администратора')
    await state.set_state(AddAdmin.username)

@admin_router.message(AddAdmin.username)
async def new_admin_username(message: types.Message, session: AsyncSession, state: FSMContext):
    admins_list = await orm_get_admins(session)

    await state.update_data(username=message.text)

    if message.text in admins_list.username:
        await message.answer(f' @{message.text} - уже является администратором',reply_markup=get_callback_btns
                             (btns={
                                 'Добавить еще администратора?': 'add_admin',
                                 'Меню главного администратора': 'admin_manage'
                                 },
                              sizes=(1,1)
                                ))
        await state.clear()
    else:
        await orm_add_admin(session, message.text)
        await message.reply(f'@{message.text} - теперь администратор',reply_markup=get_callback_btns(btns={
            'Добавить еще администратора?': 'add_admin',
            'Меню главного администратора': 'admin_manage'
            }))
        await state.clear()


######################### Отмена FSM машины #######################################

@admin_router.message(StateFilter('*'), F.text.casefold()==('отмена'))
async def cancel_handler(message: types.Message, state: FSMContext):
    currunt_state = await state.get_state()
    if currunt_state is None:
        return
    await state.clear()
    await message.answer('Отмена действия',reply_markup=get_callback_btns(
        btns={
            'Меню администратора': 'admin'
    }))


################# Микро FSM для загрузки/изменения баннеров ############################

class AddBanner(StatesGroup):
    image = State()

# Отправляем перечень информационных страниц бота и становимся в состояние отправки photo
@admin_router.callback_query(StateFilter(None), F.data == ('banner'))
async def add_image2(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await cb.message.answer(f"Отправьте фото баннера.\nВ описании укажите для какой страницы:\
                         \n{', '.join(pages_names)}")
    await state.set_state(AddBanner.image)

# Добавляем/изменяем изображение в таблице (там уже есть записанные страницы по именам:
# main, catalog, cart(для пустой корзины), about, payment, shipping
@admin_router.message(AddBanner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(f"Введите коректное название страницы, например:\
                         \n{', '.join(pages_names)}")
        return
    await orm_change_banner_image(session, for_page, image_id,)
    await message.answer("Баннер добавлен/изменен.")
    await state.clear()

# ловим некоррекный ввод
@admin_router.message(AddBanner.image)
async def error_banner(message: types.Message):
    await message.answer("Отправьте фото баннера или напишите отмена")

################## Откат к прошлому стейту ################################
@admin_router.message(F.text.casefold()==('назад'))
async def backstep(msg: types.Message,state: FSMContext):
    curstate = await state.get_state()
    if curstate == AddGame.name:
        await msg.answer(
            'Предыдущего шага нет'
        )
        return
    prev = None
    for step in AddGame.__all_states__:
        if step.state == curstate:
            await state.set_state(prev)
            await msg.answer(
                f"Вы вернулись к предыдущему шагу\n{AddGame.texts[prev.state]}"
            )
        prev = step

##################### Добавление игры #####################################

class AddGame(StatesGroup):
    name = State()
    description = State()
    category = State()
    price = State()
    image = State()
    login = State()
    password = State()
    mail = State()
    mail_password = State()

    texts = {
        'AddGame.name':'Введите название заново',
        'AddGame.description':'Введите описание заново',
        'AddGame.category':'Введите категории заново',
        'AddGame.price':'Введите цену заново',
        'AddGame.image':'Картинку заново',
        'AddGame.login':'Введите логин  заново',
        'AddGame.password':'Введите пароль заново',
        'AddGame.mail':'Введите почту заново',
        'AddGame.mail_password':'Введите imap заново'
    }


@admin_router.callback_query(StateFilter(None), F.data == ('add_game'))
async def add_game(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.reply(
        text='Введите название игры'
    )
    await state.set_state(AddGame.name)

@admin_router.message(AddGame.name)
async def add_game_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply('Введите описание игры')
    await state.set_state(AddGame.description)

@admin_router.message(AddGame.description)
async def add_game_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.reply('Введите категорию добавляемой игры')
    await state.set_state(AddGame.category)

@admin_router.message(AddGame.category)
async def add_game_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.reply('Введите цену для покупки аккаунта с игрой')
    await state.set_state(AddGame.price)

@admin_router.message(AddGame.price)
async def add_game_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.reply('Загрузите обложку игры')
    await state.set_state(AddGame.image)

@admin_router.message(AddGame.image)
async def add_image(message: types.Message, state: FSMContext):
    if message.photo:
        await state.update_data(image=message.photo[0].file_id)
    await message.reply('Введите логин от аккаунта с добавляемой игрой')
    await state.set_state(AddGame.login)

@admin_router.message(AddGame.login)
async def add_login(message: types.Message, state: FSMContext):
    await state.update_data(accnewlogin=message.text)
    await message.reply('Введите пароль от аккаунта')
    await state.set_state(AddGame.password)

@admin_router.message(AddGame.password)
async def add_password(message: types.Message,state: FSMContext):
    await state.update_data(accnewpassword=message.text)
    await message.reply('Введие почтовый адрес, на который зарегестрирован аккаунт с игрой')
    await state.set_state(AddGame.mail)

@admin_router.message(AddGame.mail)
async def add_mail(message: types.Message,state: FSMContext):
    await state.update_data(accmail=message.text)
    await message.reply('Теперь пароль от почты')
    await state.set_state(AddGame.mail_password)

@admin_router.message(AddGame.mail_password)
async def add_mail_password(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(mail_password=message.text)
    data = await state.get_data()
    await orm_add_game(session, data)

    await message.reply_photo(
        photo=data['image'],
        caption=f'Аккаунт добавлен\nНазвание: {data["name"]}\nОписание: {data['description']}\nЦена: {data["price"]} руб.',
        reply_markup=get_callback_btns(btns={
            'Добавить еще аккаунт': 'add_game',
            'Меню администратора': 'admin'
        },
        sizes=(1,1))
    )

################## Изменение/удаление аккаунтов #########################

@admin_router.callback_query(F.data == 'show_games')
async def show_games(callback: types.CallbackQuery, session: AsyncSession):
    games_list = await orm_get_games(session)

    if games_list:
        for game in games_list:
            account_info = (
                f"Название: {game.name}\n"
                f"Почта: {game.mail}\n"
                f"Цена: {game.price}"
            )
            reply_markup = get_callback_btns(btns={
                f'Изменить {game.name}': f'changeInfo_{game.name}',
                f'Удалить {game.name}': f'delete_{game.name}'
            })

            if game.image:  # Проверяем, есть ли изображение
                await callback.message.answer_photo(photo=game.image, caption=account_info, reply_markup=reply_markup)
            else:
                await callback.message.answer(account_info, reply_markup=reply_markup)
    else:
        await callback.message.answer(
            'Нет добавленных игр', reply_markup=get_callback_btns(btns={
                'Меню администора': 'admin'
            })
        )

###СМЕНА ИНФОРМАЦИИ ОБ АКАУНТЕ###
@admin_router.callback_query(F.data.startswith('changeInfo_'))
async def change_game_info(callback: types.CallbackQuery, session: AsyncSession):
    name = callback.data.split('_')[-1]

    # Получаем информацию об аккаунте из базы данных
    game = await orm_get_game(session, name)

    await callback.message.answer(
        f"Вы выбрали игру: {game.name}\n"
        f"Категория игры: {game.category}\n"
        f"Цена: {game.price} руб.\n"
        "Что вы хотите изменить?",
        reply_markup=get_callback_btns(btns={
            "Изменить игры": f"change_games_{game.name}",
            "Изменить цену": f"change_price_{game.name}",
            "Изменить описание": f"change_description_{game.name}",
            "Изменить категорию": f"change_categories_{game.name}",
            "Изменить логин": f"change_login_{game.name}",
            "Изменить пароль": f"change_password_{game.name}",
            "Изменить обложку": f"change_image_{game.name}",
            "Изменить почту": f"change_email_{game.name}",
            "Изменить пароль от почты": f"change_imap_{game.name}"
        })
    )
    await callback.answer()

###СМЕНА ИНФОРМАЦИИ ОБ АКАУНТЕ КОНКРЕТНО ПО ПУНКТАМ###
@admin_router.callback_query(F.data.startswith('change_'))
async def process_change_selection(callback: types.CallbackQuery, state: FSMContext):
    _, change_type, game_name = callback.data.split('_')[3]

    # Сохраняем имя аккаунта в состоянии
    await state.update_data(game_name=game_name)

    prompts = {
        'name': "Введите название игры:",
        'price': "Введите новую цену:",
        'description': "Введите новое описание:",
        'category': "Введите новую категорию",
        'login': "Введите новый логин:",
        'password': "Введите новый пароль:",
        'mail': "Введите новую почту:",
        'image': "Введите URL новой обложки:",
        'mail_password': "Введите новый пароль от почты:"
    }

    if change_type in prompts:
        await callback.message.answer(prompts[change_type])
        await state.set_state(f"new_{change_type}")

@admin_router.message(StateFilter(FSMContext))
async def update_field(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    game_name = data.get('game_name')

    current_state = await state.get_state()
    field_name = current_state.split("_")[1]

    await orm_update_catalog(session, game_name, field_name, message.text)

    await message.answer(f"{field_name.replace('_', ' ').capitalize()} аккаунта обновлено на: {message.text}")
    await state.clear()


######################### Удаление игры ########################################
@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_game(callback: types.CallbackQuery, session: AsyncSession):
    game_name = callback.data.split('_')[1]
    await orm_delete_game(session, game_name)
    await callback.message.answer(f'Аккаунт {game_name} удалён.')
    await callback.message.delete()


################## Удаление администратора ###############################################
@admin_router.callback_query(F.data == 'delete_admin')
async def delete_admin(callback: types.CallbackQuery, session: AsyncSession):
    admins_list = await orm_get_admins(session)

    if admins_list:
        btns = {f'Удалить @{admin.username}': f'delete_{admin.username}' for admin in admins_list}
        reply_markup = get_callback_btns(btns=btns, sizes=(2,))

        await callback.message.answer('Список администраторов:', reply_markup=reply_markup)
    else:
        await callback.message.answer('Нет администраторов.')

@admin_router.callback_query(F.data.startswith('delete_admin_'))
async def handle_delete_admin(callback: types.CallbackQuery, session: AsyncSession):
    username_to_delete = callback.data.split('_')[2]

    await orm_delete_admin(session, username_to_delete)

    await callback.message.answer(f'Администратор @{username_to_delete} удалён.')
    await callback.message.delete()
