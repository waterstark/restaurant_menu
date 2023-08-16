from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status

from src.schemas import DishModel, ResponceAllDish, ResponseDishModel, UpdateDishModel
from src.service.service import DishService

router = APIRouter(
    prefix='/api/v1/menus/{menu_id}/submenu/{submenu_id}/dishes',
    tags=['dishes'],
)


@router.post('/', response_model=ResponseDishModel, status_code=status.HTTP_201_CREATED)
async def add_dish(
    submenu_id: UUID,
    new_dish: DishModel,
    dish: Annotated[DishService, Depends()],
    menu_id: UUID,
    background_tasks: BackgroundTasks,
) -> ResponseDishModel:
    return await dish.create_dish(
        submenu_id, new_dish, menu_id, background_tasks=background_tasks,
    )


@router.get(
    '/',
    response_model=ResponceAllDish,
    status_code=status.HTTP_200_OK,
)
async def get_all_dishes(
    submenu_id: UUID,
    dishes: Annotated[DishService, Depends()],
) -> ResponceAllDish:
    return await dishes.read_all_dishes(submenu_id)


@router.get(
    '/{dish_id}',
    response_model=ResponseDishModel,
    status_code=status.HTTP_200_OK,
)
async def get_dish(
    dish_id: UUID,
    dish: Annotated[DishService, Depends()],
) -> ResponseDishModel:
    return await dish.read_dish(dish_id)


@router.patch(
    '/{dish_id}',
    response_model=ResponseDishModel,
    status_code=status.HTTP_200_OK,
)
async def upload_dish(
    submenu_id: UUID,
    dish_id: UUID,
    new_submenu: UpdateDishModel,
    dish: Annotated[DishService, Depends()],
    background_tasks: BackgroundTasks,
) -> ResponseDishModel:
    return await dish.update_dish(submenu_id, dish_id, new_submenu, background_tasks)


@router.delete('/{dish_id}', status_code=status.HTTP_200_OK)
async def removing_dish(
    dish_id: UUID,
    dish: Annotated[DishService, Depends()],
    menu_id: UUID,
    submenu_id: UUID,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    return await dish.delete_dish(dish_id, menu_id, submenu_id, background_tasks)
