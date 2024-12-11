"""Functions for work with database."""
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models import Base, Order, User

engine = create_async_engine(url="sqlite+aiosqlite:///data.db")
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


def connection(func):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                return await func(*args, session=session, **kwargs)
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    return wrapper


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@connection
async def add_user(user_id: int, username: str, session: AsyncSession) -> None:
    if not await session.scalar(select(User).where(User.user_id == user_id)):
        session.add(User(user_id=user_id, username=username))
        await session.commit()


@connection
async def get_users(session: AsyncSession) -> list:
    users = await session.scalars(select(User.user_id))
    return users.all()


@connection
async def remove_user(user_id: int, session: AsyncSession) -> None:
    await session.execute(delete(User).where(User.user_id == user_id))
    await session.commit()


@connection
async def add_last_orders(page_url: str, first_order: str, second_order: str, third_order: str, session: AsyncSession) -> None:
    page_orders = await session.scalar(select(Order).where(Order.page_url == page_url))
    if page_orders:
        page_orders.first_order = first_order
        page_orders.second_order = second_order
        page_orders.third_order = third_order
    else:
        session.add(Order(page_url=page_url, first_order=first_order, second_order=second_order, third_order=third_order))
    await session.commit()


@connection
async def get_last_orders(page_url: str, session: AsyncSession) -> list:
    query = await session.execute(
        select(Order.first_order, Order.second_order, Order.third_order)
        .where(Order.page_url == page_url),
    )
    last_orders = query.first()
    return last_orders if last_orders else []
