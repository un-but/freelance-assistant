from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]


class   Order(Base):
    __tablename__ = "orders"

    page_url: Mapped[str] = mapped_column(primary_key=True)
    first_order: Mapped[str]
    second_order: Mapped[str]
    third_order: Mapped[str]
