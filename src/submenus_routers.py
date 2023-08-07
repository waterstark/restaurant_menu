from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.schemas import (
    ResponceAllSubmenu,
    ResponseSubmenuModel,
    SubmenuModel,
    UpdateSubmenuModel,
)
from src.service.service import SubMenuService

router = APIRouter(
    prefix='/api/v1/menus/{menu_id}/submenus',
    tags=['submenus'],
)


@router.get('/', response_model=ResponceAllSubmenu, status_code=status.HTTP_200_OK)
async def get_all_submenu(
    menu_id: UUID,
    submenu: Annotated[SubMenuService, Depends()],
) -> ResponceAllSubmenu:
    return await submenu.read_all_submenus(menu_id)


@router.post(
    '/',
    response_model=ResponseSubmenuModel,
    status_code=status.HTTP_201_CREATED,
)
async def add_submenu(
    menu_id: UUID,
    new_submenu: SubmenuModel,
    submenu: Annotated[SubMenuService, Depends()],
) -> ResponseSubmenuModel:
    return await submenu.create_submenu(menu_id, new_submenu)


@router.get(
    '/{submenu_id}',
    response_model=ResponseSubmenuModel,
    status_code=status.HTTP_200_OK,
)
async def get_submenu(
    submenu_id: UUID,
    submenu: Annotated[SubMenuService, Depends()],
) -> ResponseSubmenuModel:
    return await submenu.read_submenu(submenu_id)


@router.patch(
    '/{submenu_id}',
    response_model=ResponseSubmenuModel,
    status_code=status.HTTP_200_OK,
)
async def patch_submenu(
    menu_id: UUID,
    submenu_id: UUID,
    new_submenu: UpdateSubmenuModel,
    submenu: Annotated[SubMenuService, Depends()],
) -> ResponseSubmenuModel:
    return await submenu.update_submenu(menu_id, submenu_id, new_submenu)


@router.delete('/{submenu_id}', status_code=status.HTTP_200_OK)
async def delete_submenu(
    submenu_id: UUID,
    submenu: Annotated[SubMenuService, Depends()],
    menu_id: UUID,
) -> dict[str, str]:
    return await submenu.delete_submenu(submenu_id, menu_id)
