from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_async_session
from src.models import Dishes, Menu, SubMenu
from src.schemas import MenuModel, ResponseMenuModel


class MenuCrud:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_async_session)],
    ) -> None:
        self.session = session

    async def get_all_data(self):
        query = (
            select(Menu)
            .order_by(Menu.id)
            .options(selectinload(Menu.submenu).selectinload(SubMenu.dish))
        )
        result = await self.session.execute(query)
        return result.scalars().fetchall()

    async def get_list_menus(
        self,
    ) -> Sequence[Menu]:
        query = select(Menu)
        result = await self.session.execute(query)
        return result.scalars().fetchall()

    async def create(self, new_menu: MenuModel) -> Menu:
        stmt = insert(Menu).values(**new_menu.model_dump()).returning(Menu)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_by_menu_id(self, menu_id: UUID) -> ResponseMenuModel:
        query = select(Menu).where(Menu.id == menu_id)
        result = await self.session.execute(query)
        menu = result.scalar()
        if menu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='menu not found',
            )
        submenu_count, dish_count = await self.count_submenus_and_dishes(menu_id)
        return ResponseMenuModel(
            id=menu.id,
            title=menu.title,
            description=menu.description,
            submenus_count=submenu_count,
            dishes_count=dish_count,
        )

    async def count_submenus_and_dishes(self, menu_id: UUID) -> tuple:
        stmt = (
            select(
                func.count(SubMenu.id),
                func.sum(
                    select(func.count(Dishes.id))
                    .where(SubMenu.id == Dishes.submenu_id)
                    .correlate(SubMenu)
                    .scalar_subquery(),
                ),
            )
            .select_from(Menu)
            .join(SubMenu, Menu.id == SubMenu.menu_id)
            .where(Menu.id == menu_id)
            .group_by(Menu.id)
        )

        result = await self.session.execute(stmt)
        result2 = result.first()
        if result2 is None:
            return 0, 0
        return result2.tuple()

    async def update(self, menu_id: UUID, new_menu: MenuModel) -> Menu:
        stmt = (
            update(Menu)
            .values(**new_menu.model_dump())
            .returning(Menu)
            .where(Menu.id == menu_id)
        )
        result = await self.session.execute(stmt)
        menu = result.scalar_one()
        await self.session.commit()
        return menu

    async def delete(self, menu_id: UUID):
        query = delete(Menu).where(Menu.id == menu_id)
        await self.session.execute(query)
        await self.session.commit()
