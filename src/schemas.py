from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, RootModel, field_validator


def price_format(price: float) -> str:
    return f'{price:.2f}'


class ConfigModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseRestaurantModel(ConfigModel):
    title: str
    description: str


class ResponseBaseRestaurantModel(BaseRestaurantModel):
    id: UUID


class ResponseMenuModel(ResponseBaseRestaurantModel):
    submenus_count: int = 0
    dishes_count: int = 0


class ResponseSubmenuModel(ResponseBaseRestaurantModel):
    dishes_count: int = 0


class ResponseDishModel(ResponseBaseRestaurantModel):
    price: Decimal

    _normalize_price = field_validator('price')(price_format)


class MenuModel(BaseRestaurantModel):
    pass


class SubmenuModel(BaseRestaurantModel):
    pass


class DishModel(BaseRestaurantModel):
    price: float


class UpdateRestaurantModel(ConfigModel):
    title: str | None
    description: str | None


class UpdateMenuModel(UpdateRestaurantModel):
    pass


class UpdateSubmenuModel(UpdateRestaurantModel):
    pass


class UpdateDishModel(UpdateRestaurantModel):
    price: float | None


ResponseAllMenu = RootModel[list[ResponseMenuModel]]
ResponceAllSubmenu = RootModel[list[ResponseSubmenuModel]]
ResponceAllDish = RootModel[list[ResponseDishModel]]
