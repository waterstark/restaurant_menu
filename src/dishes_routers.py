from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.schemas import DishModel, ResponceAllDish, ResponseDishModel, UpdateDishModel
from src.service.service import DishService

router = APIRouter(
    prefix='/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
    tags=['dishes'],
)


# @router.get(
#     "/", response_model=list[ResponseDishModel], status_code=status.HTTP_200_OK
# )
# async def get_submenu(session: AsyncSession = Depends(get_async_session)):
#     query = select(SubMenu)
#     result = await session.execute(query)
#     return result.scalars().fetchall()


@router.post('/', response_model=ResponseDishModel, status_code=status.HTTP_201_CREATED)
async def add_dish(
    submenu_id: UUID,
    new_dish: DishModel,
    dish: Annotated[DishService, Depends()],
    menu_id: UUID,
) -> ResponseDishModel:
    return await dish.create_dish(submenu_id, new_dish, menu_id)


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
) -> ResponseDishModel:
    return await dish.update_dish(submenu_id, dish_id, new_submenu)


@router.delete('/{dish_id}', status_code=status.HTTP_200_OK)
async def removing_dish(
    dish_id: UUID,
    dish: Annotated[DishService, Depends()],
    menu_id: UUID,
    submenu_id: UUID,
) -> dict[str, str]:
    return await dish.delete_dish(dish_id, menu_id, submenu_id)
