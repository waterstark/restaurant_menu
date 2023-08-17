from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import Dishes
from src.schemas import DishModel, UpdateDishModel


class DishCrud:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_async_session)],
    ) -> None:
        self.session = session

    async def get_list_dishes(self, submenu_id: UUID) -> Sequence[Dishes]:
        query = select(Dishes).where(Dishes.submenu_id == submenu_id)
        result = await self.session.execute(query)
        return result.scalars().fetchall()

    async def get_by_dish_id(self, dish_id: UUID) -> Dishes:
        query = select(Dishes).where(Dishes.id == dish_id)
        result = await self.session.execute(query)
        db_dish = result.scalar()
        if db_dish is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='dish not found',
            )
        return db_dish

    async def create(self, submenu_id: UUID, new_dish: DishModel, **kwargs) -> Dishes:
        stmt = (
            insert(Dishes)
            .values(**new_dish.model_dump(), submenu_id=submenu_id, **kwargs)
            .returning(Dishes)
        )
        result = await self.session.execute(stmt)
        db_dish = result.scalar_one()
        await self.session.commit()
        return db_dish

    async def update(
        self,
        submenu_id: UUID,
        dish_id: UUID,
        new_dish: UpdateDishModel,
    ) -> Dishes:
        stmt = (
            update(Dishes)
            .values(**new_dish.model_dump(), submenu_id=submenu_id)
            .returning(Dishes)
            .where(Dishes.id == dish_id)
        )

        result = await self.session.execute(stmt)
        db_dish = result.scalar_one()
        await self.session.commit()
        return db_dish

    async def delete(self, dish_id: UUID):
        await self.session.execute(delete(Dishes).where(Dishes.id == dish_id))
        await self.session.commit()
