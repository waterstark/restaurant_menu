from fastapi import FastAPI
from src.menu_routers import router as menu_router
from src.submenus_routers import router as submenu_router
from src.dishes_routers import router as dish_router

app = FastAPI(title="Menu App", docs_url="/")

app.include_router(menu_router)
app.include_router(submenu_router)
app.include_router(dish_router)
