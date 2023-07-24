from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import SubMenu, Menu, Dishes
from src.schemas import DishModel, ResponseDishModel, UpdateDishModel

from uuid import UUID

router = APIRouter(
    prefix="/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes",
    tags=["dishes"],
)


# @router.get(
#     "/", response_model=list[ResponseDishModel], status_code=status.HTTP_200_OK
# )
# async def get_submenu(session: AsyncSession = Depends(get_async_session)):
#     query = select(SubMenu)
#     result = await session.execute(query)
#     return result.scalars().fetchall()


@router.post("/", response_model=ResponseDishModel, status_code=status.HTTP_201_CREATED)
async def add_dish(
    submenu_id: UUID,
    new_dish: DishModel,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        insert(Dishes)
        .values(**new_dish.model_dump(), submenu_id=submenu_id)
        .returning(Dishes)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar()


@router.get(
    "/",
    response_model=list[ResponseDishModel],
    status_code=status.HTTP_200_OK,
)
async def get_dishes(
    submenu_id: UUID, session: AsyncSession = Depends(get_async_session)
):
    query = select(Dishes).where(Dishes.submenu_id == submenu_id)
    result = await session.execute(query)
    return result.scalars().fetchall()


@router.get(
    "/{dish_id}",
    response_model=ResponseDishModel,
    status_code=status.HTTP_200_OK,
)
async def get_submenu(
    dish_id: UUID, session: AsyncSession = Depends(get_async_session)
):
    query = select(Dishes).where(Dishes.id == dish_id)
    result = await session.execute(query)
    submenu = result.scalar()
    if not submenu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="dish not found"
        )
    return submenu


@router.patch(
    "/{dish_id}", response_model=ResponseDishModel, status_code=status.HTTP_200_OK
)
async def update_submenu(
    submenu_id: UUID,
    dish_id: UUID,
    new_submenu: UpdateDishModel,
    session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        update(Dishes)
        .values(**new_submenu.model_dump(), submenu_id=submenu_id)
        .returning(Dishes)
        .where(Dishes.id == dish_id)
    )

    result = await session.execute(stmt)
    await session.commit()
    return result.scalar()


@router.delete("/{dish_id}", status_code=status.HTTP_200_OK)
async def get_menu(dish_id: UUID, session: AsyncSession = Depends(get_async_session)):
    await session.execute(delete(Dishes).where(Dishes.id == dish_id))
    await session.commit()
