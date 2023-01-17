from pydantic import BaseModel


class MenuBase(BaseModel):
    title: str
    description: str


class MenuCreate(MenuBase):
    pass


class MenuResponse(MenuBase):
    id: int
    submenus_count: int
    dishes_count: int
