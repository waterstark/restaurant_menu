from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import Dishes, SubMenu
from src.schemas import ResponseSubmenuModel, SubmenuModel, UpdateSubmenuModel


class SubMenuCrud:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_async_session)],
    ) -> None:
        self.session = session

    async def get_list_submenu(self, menu_id: UUID) -> Sequence[SubMenu]:
        query = select(SubMenu).where(SubMenu.menu_id == menu_id)
        result = await self.session.execute(query)
        return result.scalars().fetchall()

    async def get_by_submenu_id(self, submenu_id: UUID) -> ResponseSubmenuModel:
        query = select(SubMenu).where(SubMenu.id == submenu_id)
        result = await self.session.execute(query)
        submenu = result.scalar()
        if submenu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='submenu not found',
            )
        count = await self.count_dishes(submenu_id)
        return ResponseSubmenuModel(
            title=submenu.title,
            description=submenu.description,
            dishes_count=count,
            id=submenu.id,
        )

    async def count_dishes(self, menu_id: UUID) -> int:
        stmt = (
            select(func.count(Dishes.id))
            .select_from(SubMenu)
            .join(Dishes, SubMenu.id == Dishes.submenu_id)
            .where(SubMenu.id == menu_id)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(
        self,
        menu_id: UUID,
        new_submenu: SubmenuModel,
    ) -> SubMenu:
        stmt = (
            insert(SubMenu)
            .values(**new_submenu.model_dump(), menu_id=menu_id)
            .returning(SubMenu)
        )
        result = await self.session.execute(stmt)
        submenu = result.scalar_one()
        await self.session.commit()
        return submenu

    async def update(
        self,
        menu_id: UUID,
        submenu_id: UUID,
        new_submenu: UpdateSubmenuModel,
    ) -> SubMenu:
        stmt = (
            update(SubMenu)
            .values(**new_submenu.model_dump(), menu_id=menu_id)
            .returning(SubMenu)
            .where(SubMenu.id == submenu_id)
        )
        result = await self.session.execute(stmt)
        submenu = result.scalar_one()
        await self.session.commit()
        return submenu

    async def delete(self, submenu_id: UUID):
        await self.session.execute(
            delete(Dishes).where(Dishes.submenu_id == submenu_id),
        )
        query = delete(SubMenu).where(SubMenu.id == submenu_id)
        await self.session.execute(query)
        await self.session.commit()
