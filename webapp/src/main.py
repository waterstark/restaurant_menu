from fastapi import FastAPI, Depends
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from models import Menu
from schemas import MenuBase, MenuResponse

app = FastAPI(title="Menu App")


@app.get("/api/v1/menus", tags=["menu"])
async def get_menu(session: AsyncSession = Depends(get_async_session)):
    query = select(Menu.id)
    result = await session.execute(query)
    return result.all()


@app.post("/api/v1/menus", tags=["menu"])
async def add_menu(
    new_menu: MenuBase,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = insert(Menu).values(**new_menu.dict())
    await session.execute(stmt)
    await session.commit()

    return new_menu
