import pytest

from conftest import API_URL, TEST_EMAIL, TEST_PASSWORD
from esource_client_api.models.models import Map
from esource_client_api.sync.client import SyncClient
from esource_client_api.sync.maps import Maps
from esource_client_api.sync.session import Session


@pytest.mark.integration
def test_get_all_maps():
    session = Session(API_URL, TEST_EMAIL, TEST_PASSWORD)
    maps = Maps(session)

    response = maps.list_maps()

    assert isinstance(response, list)
    assert (all(isinstance(maps, Map) for maps in response))


@pytest.mark.integration
def test_get_all_maps_using_client():
    client = SyncClient(API_URL, TEST_EMAIL, TEST_PASSWORD)

    response = client.maps.list_maps()

    assert isinstance(response, list)
    assert (all(isinstance(maps, Map) for maps in response))


@pytest.mark.integration
def test_get_map_by_id():
    session = Session(API_URL, TEST_EMAIL, TEST_PASSWORD)
    maps = Maps(session)

    response = maps.get_map(3)

    assert response.map_id == 3
    assert response.slug == "train"
    assert response.name == "Train"


@pytest.mark.integration
def test_get_map_by_name():
    session = Session(API_URL, TEST_EMAIL, TEST_PASSWORD)
    maps = Maps(session)
    response = maps.list_maps(search="Train")

    assert isinstance(response, list)
    assert response[0].map_id == 3
    assert response[0].slug == "train"
    assert response[0].name == "Train"
