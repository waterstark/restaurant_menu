from typing import Annotated
from uuid import UUID

from fastapi import BackgroundTasks, Depends
from redis import asyncio

from src.cache import get_async_redis
from src.crud.dish_crud import DishCrud
from src.crud.menu_crud import MenuCrud
from src.crud.submenu_crud import SubMenuCrud
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


async def delete_cache(cache: asyncio.Redis, *args, **kwargs):
    return await cache.delete(*args, **kwargs)


class MenuService:
    def __init__(
        self,
        cache: Annotated[asyncio.Redis, Depends(get_async_redis)],
        crud: Annotated[MenuCrud, Depends()],
    ) -> None:
        self.cache = cache
        self.crud = crud

    async def get_data(self):
        # data = MenuSchema.model_validate(await self.crud.get_all_data())
        # await self.cache.set("data", data.model_dump_json(), ex=60)
        return await self.crud.get_all_data()

    async def read_all_menus(self) -> ResponseAllMenu:
        cached_data = await self.cache.get('menu_list')
        if cached_data:
            return ResponseAllMenu.model_validate_json(cached_data)
        menu_list = ResponseAllMenu.model_validate(await self.crud.get_list_menus())
        await self.cache.set('menu_list', menu_list.model_dump_json(), ex=60)
        return menu_list

    async def create_menu(
        self,
        new_menu: MenuModel,
        background_tasks: BackgroundTasks,
    ) -> ResponseMenuModel:
        menu = await self.crud.create(new_menu)
        background_tasks.add_task(delete_cache, self.cache, f'menu_{menu.id}')
        background_tasks.add_task(delete_cache, self.cache, 'menu_list')
        return ResponseMenuModel.model_validate(menu)

    async def read_menu(self, menu_id: UUID) -> ResponseMenuModel:
        cached_data = await self.cache.get(f'menu_{menu_id}')
        if cached_data:
            return ResponseMenuModel.model_validate_json(cached_data)
        menu = await self.crud.get_by_menu_id(menu_id)
        await self.cache.set(f'menu_{menu_id}', menu.model_dump_json(), ex=60)
        return menu

    async def update_menu(
        self,
        menu_id: UUID,
        new_menu: MenuModel,
        background_tasks: BackgroundTasks,
    ) -> UpdateMenuModel:
        background_tasks.add_task(delete_cache, self.cache, 'menu_list')
        background_tasks.add_task(delete_cache, self.cache, f'menu_{menu_id}')
        return UpdateMenuModel.model_validate(await self.crud.update(menu_id, new_menu))

    async def delete_menu(
        self,
        menu_id: UUID,
        background_tasks: BackgroundTasks,
    ) -> dict[str, str]:
        background_tasks.add_task(delete_cache, self.cache, f'menu_{menu_id}')
        background_tasks.add_task(delete_cache, self.cache, 'menu_list')
        await self.crud.delete(menu_id)
        return {'status': 'succes', 'detail': 'menu deleted'}


class Submenuservice:
    def __init__(
        self,
        cache: Annotated[asyncio.Redis, Depends(get_async_redis)],
        crud: Annotated[SubMenuCrud, Depends()],
    ):
        self.cache = cache
        self.crud = crud

    async def read_all_submenu(self, menu_id: UUID) -> ResponceAllSubmenu:
        cached_data = await self.cache.get('submenu_list')
        if cached_data:
            return ResponceAllSubmenu.model_validate_json(cached_data)
        crud_submenu = await self.crud.get_list_submenu(menu_id)
        await self.cache.set(
            'submenu_list',
            ResponceAllSubmenu.model_validate(crud_submenu).model_dump_json(),
            ex=60,
        )
        return ResponceAllSubmenu.model_validate(crud_submenu)

    async def create_submenu(
        self,
        menu_id: UUID,
        new_submenu: SubmenuModel,
        background_tasks: BackgroundTasks,
    ) -> ResponseSubmenuModel:
        crud_submenu = await self.crud.create(menu_id, new_submenu)
        background_tasks.add_task(delete_cache, self.cache, f'menu_{menu_id}')
        background_tasks.add_task(delete_cache, self.cache, 'menu_list')
        background_tasks.add_task(
            delete_cache,
            self.cache,
            f'submenu_{crud_submenu.id}',
        )
        background_tasks.add_task(delete_cache, self.cache, 'submenu_list')
        return ResponseSubmenuModel.model_validate(crud_submenu)

    async def read_submenu(self, submenu_id: UUID) -> ResponseSubmenuModel:
        cached_data = await self.cache.get(f'submenu_{submenu_id}')
        if cached_data:
            return ResponseSubmenuModel.model_validate_json(cached_data)
        model_submenu = await self.crud.get_by_submenu_id(submenu_id)
        await self.cache.set(
            f'menu_{submenu_id}',
            model_submenu.model_dump_json(),
            ex=60,
        )
        return model_submenu

    async def update_submenu(
        self,
        menu_id: UUID,
        submenu_id: UUID,
        new_submenu: UpdateSubmenuModel,
        background_tasks: BackgroundTasks,
    ) -> ResponseSubmenuModel:
        crud_submenu = await self.crud.update(menu_id, submenu_id, new_submenu)
        background_tasks.add_task(delete_cache, self.cache, 'submenu_list')
        background_tasks.add_task(delete_cache, self.cache, f'submenu_{submenu_id}')
        return ResponseSubmenuModel.model_validate(crud_submenu)

    async def delete_submenu(
        self,
        submenu_id: UUID,
        menu_id: UUID,
        background_tasks: BackgroundTasks,
    ) -> dict[str, str]:
        await self.crud.delete(submenu_id)
        background_tasks.add_task(delete_cache, self.cache, f'menu_{menu_id}')
        background_tasks.add_task(delete_cache, self.cache, f'submenu_{submenu_id}')
        background_tasks.add_task(delete_cache, self.cache, 'menu_list')
        background_tasks.add_task(delete_cache, self.cache, 'submenu_list')
        background_tasks.add_task(delete_cache, self.cache, 'dish_list')
        return {'status': 'succes', 'detail': 'submenu deleted'}


class DishService:
    def __init__(
        self,
        cache: Annotated[asyncio.Redis, Depends(get_async_redis)],
        crud: Annotated[DishCrud, Depends()],
    ):
        self.cache = cache
        self.crud = crud

    async def read_all_dishes(self, submenu_id: UUID) -> ResponceAllDish:
        cached_data = await self.cache.get('dish_list')
        if cached_data:
            return ResponceAllDish.model_validate_json(cached_data)
        crud_dishes = await self.crud.get_list_dishes(submenu_id)
        await self.cache.set(
            'dish_list',
            ResponceAllDish.model_validate(crud_dishes).model_dump_json(),
            ex=60,
        )
        return ResponceAllDish.model_validate(crud_dishes)

    async def create_dish(
        self,
        submenu_id: UUID,
        new_dish: DishModel,
        menu_id: UUID,
        background_tasks: BackgroundTasks,
    ) -> ResponseDishModel:
        crud_dish = await self.crud.create(submenu_id, new_dish)
        background_tasks.add_task(delete_cache, self.cache, f'menu_{menu_id}')
        background_tasks.add_task(delete_cache, self.cache, f'submenu_{submenu_id}')
        background_tasks.add_task(delete_cache, self.cache, 'menu_list')
        background_tasks.add_task(delete_cache, self.cache, 'submenu_list')
        background_tasks.add_task(delete_cache, self.cache, 'dish_list')
        return ResponseDishModel.model_validate(crud_dish)

    async def read_dish(self, dish_id: UUID) -> ResponseDishModel:
        cached_data = await self.cache.get(f'dish_{dish_id}')
        if cached_data:
            return ResponseDishModel.model_validate_json(cached_data)
        crud_dish = await self.crud.get_by_dish_id(dish_id)
        await self.cache.set(
            f'dish_{dish_id}',
            ResponseDishModel.model_validate(crud_dish).model_dump_json(),
            ex=60,
        )
        return ResponseDishModel.model_validate(crud_dish)

    async def update_dish(
        self,
        submenu_id: UUID,
        dish_id: UUID,
        new_submenu: UpdateDishModel,
        background_tasks: BackgroundTasks,
    ) -> ResponseDishModel:
        crud_dish = await self.crud.update(submenu_id, dish_id, new_submenu)
        background_tasks.add_task(delete_cache, self.cache, 'dish_list')
        background_tasks.add_task(delete_cache, self.cache, f'dish_{dish_id}')
        return ResponseDishModel.model_validate(crud_dish)

    async def delete_dish(
        self,
        dish_id: UUID,
        menu_id: UUID,
        submenu_id: UUID,
        background_tasks: BackgroundTasks,
    ) -> dict[str, str]:
        await self.crud.delete(dish_id)
        background_tasks.add_task(delete_cache, self.cache, f'menu_{menu_id}')
        background_tasks.add_task(delete_cache, self.cache, f'submenu_{submenu_id}')
        background_tasks.add_task(delete_cache, self.cache, 'menu_list')
        background_tasks.add_task(delete_cache, self.cache, 'submenu_list')
        background_tasks.add_task(delete_cache, self.cache, 'dish_list')
        background_tasks.add_task(delete_cache, self.cache, f'dish_{dish_id}')
        return {'status': 'succes', 'detail': 'dish deleted'}
