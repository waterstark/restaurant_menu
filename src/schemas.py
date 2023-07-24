from pydantic import BaseModel, validator
from uuid import UUID


def price_format(price: float) -> str:
    return f"{price:.2f}"


class ConfigModel(BaseModel):
    class Config:
        from_attributes = True


class BaseRestaurantModel(ConfigModel):
    title: str
    description: str


class ResponseBaseRestaurantModel(BaseRestaurantModel):
    id: UUID


class ResponseMenuModel(ResponseBaseRestaurantModel):
    submenus_count: int = 0
    dishes_count: int = 0


class ResponseListMenuModel(ResponseMenuModel):
    pass


class ResponseSubmenuModel(ResponseBaseRestaurantModel):
    dishes_count: int = 0


class ResponseDishModel(ResponseBaseRestaurantModel):
    price: float

    _normalize_price = validator("price", allow_reuse=True)(price_format)


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
