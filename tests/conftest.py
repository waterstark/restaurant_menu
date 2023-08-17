import asyncio
from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from src.database import Base, get_async_session
from src.main import app
from src.schemas import ResponseDishModel, ResponseMenuModel, ResponseSubmenuModel

DATABASE_URL_TEST = (
    f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base.metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        pass


@pytest.fixture(scope='session')
def event_loop(request: type[pytest.FixtureRequest]):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.fixture()
async def default_menu(ac: AsyncClient) -> ResponseMenuModel:
    return ResponseMenuModel.model_validate(
        (
            await ac.post(
                '/api/v1/menus/',
                json={
                    'title': 'summer menu',
                    'description': 'menu',
                },
            )
        ).json(),
    )


@pytest.fixture()
async def default_submenu(
    ac: AsyncClient,
    default_menu: ResponseMenuModel,
) -> ResponseSubmenuModel:
    return ResponseSubmenuModel.model_validate(
        (
            await ac.post(
                f'/api/v1/menus/{default_menu.id}/submenu/',
                json={
                    'title': 'georgian dishes',
                    'description': 'georgian dishes',
                },
            )
        ).json(),
    )


@pytest.fixture()
async def default_dish(
    ac: AsyncClient,
    default_menu: ResponseMenuModel,
    default_submenu: ResponseSubmenuModel,
) -> ResponseDishModel:
    return ResponseDishModel.model_validate(
        (
            await ac.post(
                f'/api/v1/menus/{default_menu.id}/submenu/{default_submenu.id}/dishes/',
                json={
                    'title': 'kharcho',
                    'description': 'hearty soup',
                    'price': 100.25,
                },
            )
        ).json(),
    )
