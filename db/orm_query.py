from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Admin, Game, Banner

############### Работа с баннерами (информационными страницами) ###############

async def orm_add_banner_description(session: AsyncSession, data: dict):
    #Добавляем новый или изменяем существующий по именам
    #пунктов меню: main, about, cart, shipping, payment, catalog
    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Banner(name=name, description=description) for name, description in data.items()])
    await session.commit()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_info_pages(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_add_game(session: AsyncSession, data: dict):
    obj = Game(
        name = data["name"],
        description=data['description'],
        category=data['category'],
        price=data['price'],
        image=data['image'],
        login=data['login'],
        password=data['password'],
        mail = data['mail'],
        mail_password=data['mail_password']
    )
    session.add(obj)
    await session.commit()

async def orm_get_games(session: AsyncSession):
    query = select(Game)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_games_by_category(session: AsyncSession, category: str):
    query = select(Game).where(Game.category == category )
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_game(session: AsyncSession, game: str):
    query = select(Game).where(Game.name == game)
    result = await session.execute(query)
    return result.scalar()

async def orm_get_admins(session: AsyncSession):
    query = select(Admin)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_admin(session: AsyncSession, username: str):
    query = select(Admin).where(Admin.username == username)
    result = await session.execute(query)
    return result.scalar()

async def orm_add_admin(session: AsyncSession, username: str):
    obj = Admin(username = username)
    session.add(obj)
    await session.commit()

async def orm_delete_game(session: AsyncSession, name : str):
    query = delete(Game).where(Game.description == name)
    await session.execute(query)
    session.commit()

async def orm_delete_admin(session: AsyncSession, username_to_delete : str):
    query = delete(Admin).where(Admin.username == username_to_delete)
    await session.execute(query)
    session.commit()

async def orm_update_catalog(session: AsyncSession, account_name : str, field_name: str, new_value: str ):
    query = update(Game).where(Game.description == account_name).values({field_name: new_value})
    await session.execute(query)
    await session.commit()
