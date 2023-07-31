from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import SubMenu, Menu, Dishes
from src.schemas import ResponseSubmenuModel, SubmenuModel, UpdateSubmenuModel

from uuid import UUID

router = APIRouter(
    prefix="/api/v1/menus/{menu_id}/submenus",
    tags=["submenus"],
)


@router.get(
    "/", response_model=list[ResponseSubmenuModel], status_code=status.HTTP_200_OK
)
async def get_all_submenu(
    menu_id: UUID, session: AsyncSession = Depends(get_async_session)
):
    query = select(SubMenu).where(SubMenu.menu_id == menu_id)
    result = await session.execute(query)
    return result.scalars().fetchall()


@router.post(
    "/", response_model=ResponseSubmenuModel, status_code=status.HTTP_201_CREATED
)
async def add_submenu(
    menu_id: UUID,
    new_submenu: SubmenuModel,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        insert(SubMenu)
        .values(**new_submenu.model_dump(), menu_id=menu_id)
        .returning(SubMenu)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar()


@router.get(
    "/{submenu_id}",
    response_model=ResponseSubmenuModel,
    status_code=status.HTTP_200_OK,
)
async def get_submenu(
    submenu_id: UUID, session: AsyncSession = Depends(get_async_session)
):
    query = select(SubMenu).where(SubMenu.id == submenu_id)
    result = await session.execute(query)
    submenu = result.scalar()
    if not submenu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="submenu not found"
        )
    count = await count_dishes(submenu_id, session)
    return {**submenu.__dict__, "dishes_count": count}


@router.patch(
    "/{submenu_id}", response_model=ResponseSubmenuModel, status_code=status.HTTP_200_OK
)
async def update_submenu(
    menu_id: UUID,
    submenu_id: UUID,
    new_submenu: UpdateSubmenuModel,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        update(SubMenu)
        .values(**new_submenu.model_dump(), menu_id=menu_id)
        .returning(SubMenu)
        .where(SubMenu.id == submenu_id)
    )

    result = await session.execute(stmt)
    await session.commit()
    return result.scalar()


@router.delete("/{submenu_id}", status_code=status.HTTP_200_OK)
async def delete_submenu(
    submenu_id: UUID, session: AsyncSession = Depends(get_async_session)
):
    await session.execute(delete(Dishes).where(Dishes.submenu_id == submenu_id))
    query = delete(SubMenu).where(SubMenu.id == submenu_id)
    await session.execute(query)
    await session.commit()


async def count_dishes(menu_id, session):
    stmt = (
        select(func.count(Dishes.id))
        .select_from(SubMenu)
        .join(Dishes, SubMenu.id == Dishes.submenu_id)
        .where(SubMenu.id == menu_id)
    )

    result = await session.execute(stmt)

    return result.scalar()
