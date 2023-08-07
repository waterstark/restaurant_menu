from dirty_equals import IsUUID
from httpx import AsyncClient

from src.schemas import ResponseDishModel, ResponseMenuModel, ResponseSubmenuModel


async def test_get_all_dishes(
    ac: AsyncClient,
    default_menu: ResponseMenuModel,
    default_submenu: ResponseSubmenuModel,
):
    resp = await ac.get(
        f'/api/v1/menus/{default_menu.id}/submenus/{default_submenu.id}/dishes/',
    )
    # insert_assert(resp.status_code)
    assert resp.status_code == 200
    # insert_assert(resp.json())
    assert resp.json() == []


async def test_add_dish(
    ac: AsyncClient,
    default_menu: ResponseMenuModel,
    default_submenu: ResponseSubmenuModel,
):
    resp = await ac.post(
        f'/api/v1/menus/{default_menu.id}/submenus/{default_submenu.id}/dishes/',
        json=(
            {
                'submenu_id': str(default_submenu.id),
                'title': 'menu',
                'description': 'menu',
                'price': '100.57',
            }
        ),
    )
    assert resp.status_code == 201
    assert resp.json() == {
        'title': 'menu',
        'description': 'menu',
        'id': IsUUID(4),
        'price': '100.57',
    }


async def test_get_dish(
    ac: AsyncClient,
    default_menu: ResponseMenuModel,
    default_submenu: ResponseSubmenuModel,
    default_dish: ResponseDishModel,
):
    resp = await ac.get(
        f'/api/v1/menus/{default_menu.id}/submenus/{default_submenu.id}/dishes/{default_dish.id}',
    )
    # insert_assert(resp.status_code)
    assert resp.status_code == 200
    # insert_assert(resp.json())
    assert resp.json() == {
        'title': 'kharcho',
        'description': 'hearty soup',
        'id': IsUUID(4),
        'price': '100.25',
    }


async def test_update_dish(
    ac: AsyncClient,
    default_submenu: ResponseMenuModel,
    default_menu: ResponseSubmenuModel,
    default_dish: ResponseDishModel,
):
    resp = await ac.patch(
        f'/api/v1/menus/{default_menu.id}/submenus/{default_submenu.id}/dishes/{default_dish.id}',
        json={
            'title': 'another submenu',
            'description': 'submenu description',
            'price': '110.25',
        },
    )
    # insert_assert(resp.status_code)
    assert resp.status_code == 200
    # insert_assert(resp.json())
    assert resp.json() == {
        'title': 'another submenu',
        'description': 'submenu description',
        'id': IsUUID(4),
        'price': '110.25',
    }


async def test_delete_dish(
    ac: AsyncClient,
    default_menu: ResponseMenuModel,
    default_submenu: ResponseSubmenuModel,
    default_dish: ResponseDishModel,
):
    resp = await ac.delete(
        f'/api/v1/menus/{default_menu.id}/submenus/{default_submenu.id}/dishes/{default_dish.id}',
    )
    # insert_assert(resp.status_code)
    assert resp.status_code == 200

    result = await ac.get(
        f'/api/v1/menus/{default_menu.id}/submenus/{default_submenu.id}/dishes/{default_dish.id}',
    )
    assert result.status_code == 404
