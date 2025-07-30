import pytest

from esource_client_api.async_.client import AsyncClient
from esource_client_api.async_.maps import Maps
from esource_client_api.async_.session import AsyncSession
from conftest import API_URL, TEST_EMAIL, TEST_PASSWORD
from esource_client_api.models.models import Map


@pytest.mark.asyncio
@pytest.mark.integration
async def test_ascync_get_all_maps():
    async with AsyncSession(API_URL, TEST_EMAIL, TEST_PASSWORD) as session:
        await session.login()
        maps = Maps(session)

        response = await maps.list_maps()

        assert isinstance(response, list)
        assert (all(isinstance(maps, Map) for maps in response))


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_maps_using_client():
    client = AsyncClient(API_URL, TEST_EMAIL, TEST_PASSWORD)
    await client.login()

    response = await client.maps.list_maps()

    assert isinstance(response, list)
    assert (all(isinstance(maps, Map) for maps in response))


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_get_map_by_id():
    async with AsyncSession(API_URL, TEST_EMAIL, TEST_PASSWORD) as session:
        await session.login()
        maps = Maps(session)

        response = await maps.get_map(3)

        assert response.map_id == 3
        assert response.slug == "train"
        assert response.name == "Train"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_get_map_by_name():
    async with AsyncSession(API_URL, TEST_EMAIL, TEST_PASSWORD) as session:
        await session.login()
        maps = Maps(session)
        response = await maps.list_maps(search="Train")

        assert isinstance(response, list)
        assert response[0].map_id == 3
        assert response[0].slug == "train"
        assert response[0].name == "Train"
