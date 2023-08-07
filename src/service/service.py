from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache import get_async_redis
from src.database import get_async_session
from src.models import Dishes, Menu, SubMenu
from src.schemas import (
    DishModel,
    MenuModel,
    ResponceAllDish,
    ResponceAllSubmenu,
    ResponseAllMenu,
    ResponseDishModel,
    ResponseMenuModel,
    ResponseSubmenuModel,
    SubmenuModel,
    UpdateDishModel,
    UpdateMenuModel,
    UpdateSubmenuModel,
)


class MenuService:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        cache: Annotated[AsyncSession, Depends(get_async_redis)],
    ):
        self.session = session
        self.cache = cache

    async def read_all_menus(self) -> ResponseAllMenu:
        cached_data = await self.cache.get('menu_list')
        if cached_data:
            return ResponseAllMenu.model_validate_json(cached_data)
        query = select(Menu)
        result = await self.session.execute(query)
        db_menus = result.scalars().fetchall()
        await self.cache.set(
            'menu_list',
            ResponseAllMenu.model_validate(db_menus).model_dump_json(),
        )
        return ResponseAllMenu.model_validate(db_menus)

    async def create_menu(
        self,
        new_menu: MenuModel,
    ) -> ResponseMenuModel:
        stmt = insert(Menu).values(**new_menu.model_dump()).returning(Menu)
        result = await self.session.execute(stmt)
        await self.session.commit()
        await self.cache.delete('menu_list')
        return ResponseMenuModel.model_validate(result.scalar())

    async def read_menu(self, menu_id: UUID) -> ResponseMenuModel:
        cached_data = await self.cache.get(f'menu_{menu_id}')
        if cached_data:
            return ResponseMenuModel.model_validate_json(cached_data)
        query = select(Menu).where(Menu.id == menu_id)
        result = await self.session.execute(query)
        menu = result.scalar()
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='menu not found',
            )
        submenu_count, dish_count = await self.count_submenus_and_dishes(menu_id)
        model_menu = ResponseMenuModel(
            id=menu.id,
            title=menu.title,
            description=menu.description,
            submenus_count=submenu_count,
            dishes_count=dish_count,
        )
        await self.cache.set(f'menu_{menu_id}', model_menu.model_dump_json())
        return model_menu

    async def count_submenus_and_dishes(self, menu_id) -> tuple:
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
        else:
            return result2

    async def update_menu(self, menu_id: UUID, new_menu: MenuModel) -> UpdateMenuModel:
        stmt = (
            update(Menu)
            .values(**new_menu.model_dump())
            .returning(Menu)
            .where(Menu.id == menu_id)
        )
        result = await self.session.execute(stmt)
        menu = result.scalar()
        await self.session.commit()
        # await self.cache.set(
        #     f"menu_{menu_id}",
        #     UpdateMenuModel.model_validate(menu).model_dump_json(),
        # )
        await self.cache.delete('menu_list')
        await self.cache.delete(f'menu_{menu_id}')
        return UpdateMenuModel.model_validate(menu)

    async def delete_menu(self, menu_id: UUID) -> dict[str, str]:
        query = delete(Menu).where(Menu.id == menu_id)
        await self.session.execute(query)
        await self.session.commit()
        await self.cache.delete(f'menu_{menu_id}')
        await self.cache.delete('menu_list')
        return {'status': 'succes', 'detail': 'menu deleted'}


class SubMenuService:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        cache: Annotated[AsyncSession, Depends(get_async_redis)],
    ):
        self.session = session
        self.cache = cache

    async def read_all_submenus(self, menu_id: UUID) -> ResponceAllSubmenu:
        cached_data = await self.cache.get('submenu_list')
        if cached_data:
            return ResponceAllSubmenu.model_validate_json(cached_data)
        query = select(SubMenu).where(SubMenu.menu_id == menu_id)
        result = await self.session.execute(query)
        db_submenu = result.scalars().fetchall()
        await self.cache.set(
            'submenu_list',
            ResponceAllSubmenu.model_validate(db_submenu).model_dump_json(),
        )
        return ResponceAllSubmenu.model_validate(db_submenu)

    async def create_submenu(
        self, menu_id: UUID, new_submenu: SubmenuModel,
    ) -> ResponseSubmenuModel:
        stmt = (
            insert(SubMenu)
            .values(**new_submenu.model_dump(), menu_id=menu_id)
            .returning(SubMenu)
        )
        result = await self.session.execute(stmt)
        submenu = result.scalar_one()
        await self.session.commit()
        await self.cache.delete(f'menu_{menu_id}')
        await self.cache.delete(f'submenu_{submenu.id}')
        await self.cache.delete('submenu_list')
        await self.cache.delete('menu_list')
        return ResponseSubmenuModel.model_validate(submenu)

    async def read_submenu(self, submenu_id: UUID) -> ResponseSubmenuModel:
        cached_data = await self.cache.get(f'submenu_{submenu_id}')
        if cached_data:
            return ResponseSubmenuModel.model_validate_json(cached_data)
        query = select(SubMenu).where(SubMenu.id == submenu_id)
        result = await self.session.execute(query)
        submenu = result.scalar()
        if submenu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='submenu not found',
            )
        count = await self.count_dishes(submenu_id)
        print(count)
        model_submenu = ResponseSubmenuModel(
            title=submenu.title,
            description=submenu.description,
            dishes_count=count,
            id=submenu.id,
        )
        await self.cache.set(
            f'menu_{submenu_id}',
            model_submenu.model_dump_json(),
        )
        return model_submenu

    async def count_dishes(self, menu_id: UUID):
        stmt = (
            select(func.count(Dishes.id))
            .select_from(SubMenu)
            .join(Dishes, SubMenu.id == Dishes.submenu_id)
            .where(SubMenu.id == menu_id)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update_submenu(
        self, menu_id: UUID, submenu_id: UUID, new_submenu: UpdateSubmenuModel,
    ) -> ResponseSubmenuModel:
        stmt = (
            update(SubMenu)
            .values(**new_submenu.model_dump(), menu_id=menu_id)
            .returning(SubMenu)
            .where(SubMenu.id == submenu_id)
        )

        result = await self.session.execute(stmt)
        submenu = result.scalar_one()
        await self.session.commit()
        # await self.cache.set(
        #     (f"submenu_{submenu_id}"),
        #     UpdateMenuModel.model_validate(submenu).model_dump_json(),
        # )
        await self.cache.delete('submenu_list')
        await self.cache.delete(f'submenu_{submenu_id}')
        return ResponseSubmenuModel.model_validate(submenu)

    async def delete_submenu(self, submenu_id: UUID, menu_id: UUID) -> dict[str, str]:
        await self.session.execute(
            delete(Dishes).where(Dishes.submenu_id == submenu_id),
        )
        query = delete(SubMenu).where(SubMenu.id == submenu_id)
        await self.session.execute(query)
        await self.session.commit()
        await self.cache.delete(f'menu_{menu_id}')
        await self.cache.delete(f'submenu_{submenu_id}')
        await self.cache.delete('menu_list')
        await self.cache.delete('submenu_list')
        await self.cache.delete('dish_list')
        return {'status': 'succes', 'detail': 'submenu deleted'}


class DishService:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        cache: Annotated[AsyncSession, Depends(get_async_redis)],
    ):
        self.session = session
        self.cache = cache

    async def read_all_dishes(self, submenu_id: UUID) -> ResponceAllDish:
        cached_data = await self.cache.get('dish_list')
        if cached_data:
            return ResponceAllDish.model_validate_json(cached_data)
        query = select(Dishes).where(Dishes.submenu_id == submenu_id)
        result = await self.session.execute(query)
        db_dish = result.scalars().fetchall()
        await self.cache.set(
            'dish_list',
            ResponceAllDish.model_validate(db_dish).model_dump_json(),
        )
        return ResponceAllDish.model_validate(db_dish)

    async def create_dish(
        self, submenu_id: UUID, new_dish: DishModel, menu_id: UUID,
    ) -> ResponseDishModel:
        stmt = (
            insert(Dishes)
            .values(**new_dish.model_dump(), submenu_id=submenu_id)
            .returning(Dishes)
        )
        result = await self.session.execute(stmt)
        dish = result.scalar_one()
        await self.session.commit()
        await self.cache.delete(f'menu_{menu_id}')
        await self.cache.delete(f'submenu_{submenu_id}')
        await self.cache.delete('menu_list')
        await self.cache.delete('submenu_list')
        await self.cache.delete('dish_list')
        return ResponseDishModel.model_validate(dish)

    async def read_dish(self, dish_id: UUID) -> ResponseDishModel:
        cached_data = await self.cache.get(f'dish_{dish_id}')
        if cached_data:
            return ResponseDishModel.model_validate_json(cached_data)
        query = select(Dishes).where(Dishes.id == dish_id)
        result = await self.session.execute(query)
        db_dish = result.scalar()
        if db_dish is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='dish not found',
            )
        await self.cache.set(
            f'dish_{dish_id}',
            ResponseDishModel.model_validate(db_dish).model_dump_json(),
        )
        return ResponseDishModel.model_validate(db_dish)

    async def update_dish(
        self, submenu_id: UUID, dish_id: UUID, new_submenu: UpdateDishModel,
    ) -> ResponseDishModel:
        stmt = (
            update(Dishes)
            .values(**new_submenu.model_dump(), submenu_id=submenu_id)
            .returning(Dishes)
            .where(Dishes.id == dish_id)
        )

        result = await self.session.execute(stmt)
        dish = result.scalar()
        await self.session.commit()
        # await self.cache.set(
        #     f"dish_{dish_id}",
        #     UpdateMenuModel.model_validate(dish).model_dump_json(),
        # )
        await self.cache.delete('dish_list')
        await self.cache.delete(f'dish_{dish_id}')
        return ResponseDishModel.model_validate(dish)

    async def delete_dish(
        self, dish_id: UUID, menu_id: UUID, submenu_id: UUID,
    ) -> dict[str, str]:
        await self.session.execute(delete(Dishes).where(Dishes.id == dish_id))
        await self.session.commit()
        await self.cache.delete(f'menu_{menu_id}')
        await self.cache.delete(f'submenu_{submenu_id}')
        await self.cache.delete(f'dish_{dish_id}')
        await self.cache.delete('menu_list')
        await self.cache.delete('submenu_list')
        await self.cache.delete('dish_list')
        return {'status': 'succes', 'detail': 'dish deleted'}
