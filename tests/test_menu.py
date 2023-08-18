from dirty_equals import IsUUID
from httpx import AsyncClient

from src.schemas import ResponseDishModel, ResponseMenuModel


async def test_get_all_menus(ac: AsyncClient):
    resp = await ac.get('/api/v1/menus/')
    assert resp.status_code == 200
    # insert_assert(resp.json())
    assert resp.json() == []


async def test_get_all_data(ac: AsyncClient, default_dish: ResponseDishModel):
    resp = await ac.get('/api/v1/menus/data')
    assert resp.status_code == 200
    # insert_assert(resp.json())
    assert resp.json() == [
        {
            'title': 'summer menu',
            'description': 'menu',
            'submenu': [
                {
                    'title': 'georgian dishes',
                    'description': 'georgian dishes',
                    'dishes': [
                        {
                            'title': 'kharcho',
                            'description': 'hearty soup',
                            'price': '100.25',
                        }
                    ],
                }
            ],
            'id': IsUUID(4),
        }
    ]


async def test_add_menu(ac: AsyncClient):
    resp = await ac.post(
        '/api/v1/menus/',
        json={
            'title': 'menu',
            'description': 'menu',
        },
    )
    assert resp.status_code == 201
    # insert_assert(resp.json())
    assert resp.json() == {
        'title': 'menu',
        'description': 'menu',
        'id': IsUUID(4),
        'submenu_count': 0,
        'dishes_count': 0,
    }


async def test_get_menu(ac: AsyncClient, default_menu: ResponseMenuModel):
    resp = await ac.get(f'/api/v1/menus/{default_menu.id}')
    assert resp.status_code == 200
    # insert_assert(resp.json())
    assert resp.json() == {
        'title': default_menu.title,
        'description': 'menu',
        'id': IsUUID(4),
        'submenu_count': 0,
        'dishes_count': 0,
    }


async def test_update_menu(ac: AsyncClient, default_menu: ResponseMenuModel):
    resp = await ac.patch(
        f'/api/v1/menus/{default_menu.id}',
        json={
            'title': 'winter menu',
            'description': 'menu',
        },
    )
    assert resp.status_code == 200
    # insert_assert(resp.json())
    assert resp.json() == {'title': 'winter menu', 'description': 'menu'}


async def test_delete_menu(ac: AsyncClient, default_menu: ResponseMenuModel):
    resp = await ac.delete(f'/api/v1/menus/{default_menu.id}')
    # insert_assert(resp.status_code)
    assert resp.status_code == 200

    result = await ac.get(f'/api/v1/menus/{default_menu.id}')
    assert result.status_code == 404
