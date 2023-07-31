from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.database import get_async_session
from src.models import Dishes, Menu, SubMenu
from src.schemas import (
    ResponseMenuModel,
    ResponseListMenuModel,
    MenuModel,
    UpdateMenuModel,
)

from uuid import UUID

router = APIRouter(
    prefix="/api/v1/menus",
    tags=["menu"],
)


@router.get(
    "/", response_model=list[ResponseListMenuModel], status_code=status.HTTP_200_OK
)
async def get_all_menus(session: AsyncSession = Depends(get_async_session)):
    query = select(Menu)
    result = await session.execute(query)
    return result.scalars().fetchall()


@router.post("/", response_model=ResponseMenuModel, status_code=status.HTTP_201_CREATED)
async def add_menu(
    new_menu: MenuModel,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = insert(Menu).values(**new_menu.model_dump()).returning(Menu)
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar()


@router.get(
    "/{menu_id}", response_model=ResponseMenuModel, status_code=status.HTTP_200_OK
)
async def get_menu(menu_id: UUID, session: AsyncSession = Depends(get_async_session)):
    query = select(Menu).where(Menu.id == menu_id)
    result = await session.execute(query)
    menu = result.scalar()
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="menu not found"
        )
    submenu_count, dish_count = await count_submenus_and_dishes(menu_id, session)
    return {
        **(menu.__dict__),
        "submenus_count": submenu_count,
        "dishes_count": dish_count,
    }


@router.patch(
    "/{menu_id}", response_model=UpdateMenuModel, status_code=status.HTTP_200_OK
)
async def update_menu(
    menu_id: UUID,
    new_menu: MenuModel,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        update(Menu)
        .values(**new_menu.model_dump())
        .returning(Menu)
        .where(Menu.id == menu_id)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar()


@router.delete("/{menu_id}", status_code=status.HTTP_200_OK)
async def delete_menu(
    menu_id: UUID, session: AsyncSession = Depends(get_async_session)
):
    query = delete(Menu).where(Menu.id == menu_id)
    await session.execute(query)
    await session.commit()


async def count_submenus_and_dishes(menu_id, session: AsyncSession):
    stmt = (
        select(
            func.count(SubMenu.id),
            func.sum(
                select(func.count(Dishes.id))
                .where(SubMenu.id == Dishes.submenu_id)
                .correlate(SubMenu)
                .scalar_subquery()
            ),
        )
        .select_from(Menu)
        .join(SubMenu, Menu.id == SubMenu.menu_id)
        .where(Menu.id == menu_id)
        .group_by(Menu.id)
    )

    result = await session.execute(stmt)
    result2 = result.first()
    if result2 is None:
        return 0, 0
    else:
        return result2
