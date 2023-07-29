from typing import Any

import pytest

from fyyur.routes.artist import find_artists, get_artists
from fyyur.schema.artist import ArtistWithName
from fyyur.schema.base import SearchSchema
from tests.mock import mock_artists


def test_get_artists(app):
    with app.app_context():
        artists = [ArtistWithName.model_validate(artist) for artist in mock_artists()]
        all_artists = get_artists()
        assert artists == all_artists


def test_get_aritsts_status_200(client):
    assert client.get("/artists/").status_code == 200


@pytest.mark.parametrize(
    "search_term, expected_result",
    [
        ("1", [{"id": 1, "name": "Artist1", "num_upcoming_shows": 2}]),
        ("2", [{"id": 2, "name": "Artist2", "num_upcoming_shows": 1}]),
        ("3", [{"id": 3, "name": "Artist3", "num_upcoming_shows": 1}]),
    ],
)
def test_basic_find_artists(
    app, client, search_term: str, expected_result: list[dict[str, Any]]
):
    search_schema = SearchSchema(search_term=search_term)
    with app.app_context():
        artists = find_artists(search_schema)
    assert artists == expected_result

    response = client.post("/artists/search", data=search_schema.model_dump())
    assert response.status_code == 200
