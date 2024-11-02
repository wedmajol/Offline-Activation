from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime,  Text, func

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default = func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default = func.now() , onupdate= func.now())

##################Дтаблица админов################################################################
class Admin(Base):
    __tablename__ = 'admin'

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    username: Mapped[str] = mapped_column(String)


##################таблица аккаунтов################################################################
class Game(Base):
    __tablename__ = 'game'

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[int]  = mapped_column(Integer)
    image: Mapped[str] = mapped_column(String)
    login: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    mail: Mapped[str] = mapped_column(String)
    mail_password: Mapped[str] = mapped_column(String)

##################таблица банеры ################################################################
class Banner(Base):
    __tablename__ = 'banner'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(15), unique=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
