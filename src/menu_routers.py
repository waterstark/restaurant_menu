from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status

from src.schemas import (
    MenuModel,
    ResponceAllMenus,
    ResponseAllMenu,
    ResponseMenuModel,
    UpdateMenuModel,
)
from src.service.service import MenuService

router = APIRouter(
    prefix='/api/v1/menus',
    tags=['menu'],
)


@router.get('/data', response_model=ResponceAllMenus, status_code=status.HTTP_200_OK)
async def get_all_data(menu: Annotated[MenuService, Depends()]) -> ResponceAllMenus:
    return await menu.get_data()


@router.get('/', response_model=ResponseAllMenu, status_code=status.HTTP_200_OK)
async def get_all_menus(menu: Annotated[MenuService, Depends()]) -> ResponseAllMenu:
    return await menu.read_all_menus()


@router.post('/', response_model=ResponseMenuModel, status_code=status.HTTP_201_CREATED)
async def add_menu(
    new_menu: MenuModel,
    menu: Annotated[MenuService, Depends()],
    background_tasks: BackgroundTasks,
) -> ResponseMenuModel:
    return await menu.create_menu(new_menu, background_tasks)


@router.get(
    '/{menu_id}',
    response_model=ResponseMenuModel,
    status_code=status.HTTP_200_OK,
)
async def get_menu(
    menu_id: UUID,
    menu: Annotated[MenuService, Depends()],
) -> ResponseMenuModel:
    return await menu.read_menu(menu_id)


@router.patch(
    '/{menu_id}',
    response_model=UpdateMenuModel,
    status_code=status.HTTP_200_OK,
)
async def patch_menu(
    menu_id: UUID,
    new_menu: MenuModel,
    menu: Annotated[MenuService, Depends()],
    background_tasks: BackgroundTasks,
) -> UpdateMenuModel:
    return await menu.update_menu(menu_id, new_menu, background_tasks)


@router.delete('/{menu_id}', status_code=status.HTTP_200_OK)
async def delete_menu(
    menu_id: UUID,
    menu: Annotated[MenuService, Depends()],
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    return await menu.delete_menu(menu_id, background_tasks)
