from dirty_equals import IsUUID
from httpx import AsyncClient

from src.schemas import ResponseMenuModel, ResponseSubmenuModel


async def test_get_all_submenus(ac: AsyncClient, default_menu: ResponseMenuModel):
    resp = await ac.get(f'/api/v1/menus/{default_menu.id}/submenus/')
    # insert_assert(resp.status_code)
    assert resp.status_code == 200
    # insert_assert(resp.json())
    assert resp.json() == []


async def test_add_submenu(
    ac: AsyncClient,
    default_menu: ResponseMenuModel,
):
    resp = await ac.post(
        f'/api/v1/menus/{default_menu.id}/submenus/',
        json={
            'title': 'menu',
            'description': 'menu',
        },
    )
    # insert_assert(resp.status_code)
    assert resp.status_code == 201
    # insert_assert(resp.json())
    assert resp.json() == {
        'title': 'menu',
        'description': 'menu',
        'id': IsUUID(4),
        'dishes_count': 0,
    }


async def test_get_submenu(
    ac: AsyncClient,
    default_menu: ResponseMenuModel,
    default_submenu: ResponseSubmenuModel,
):
    resp = await ac.get(
        f'/api/v1/menus/{default_menu.id}/submenus/{default_submenu.id}',
    )
    # insert_assert(resp.status_code)
    assert resp.status_code == 200
    # insert_assert(resp.json())
    assert resp.json() == {
        'title': 'georgian dishes',
        'description': 'georgian dishes',
        'id': IsUUID(4),
        'dishes_count': 0,
    }


async def test_update_submenu(
    ac: AsyncClient,
    default_submenu: ResponseMenuModel,
    default_menu: ResponseSubmenuModel,
):
    resp = await ac.patch(
        f'/api/v1/menus/{default_menu.id}/submenus/{default_submenu.id}',
        json={
            'title': 'another submenu',
            'description': 'submenu description',
        },
    )
    # insert_assert(resp.status_code)
    assert resp.status_code == 200
    # insert_assert(resp.json())
    assert resp.json() == {
        'title': 'another submenu',
        'description': 'submenu description',
        'id': IsUUID(4),
        'dishes_count': 0,
    }


async def test_delete_menu(
    ac: AsyncClient,
    default_menu: ResponseMenuModel,
    default_submenu: ResponseSubmenuModel,
):
    resp = await ac.delete(
        f'/api/v1/menus/{default_menu.id}/submenus/{default_submenu.id}',
    )
    # insert_assert(resp.status_code)
    assert resp.status_code == 200

    result = await ac.get(
        f'/api/v1/menus/{default_menu.id}/submenus/{default_submenu.id}',
    )
    assert result.status_code == 404
