from typing import Any

import pytest

from fyyur.model import db
from fyyur.routes.artist import find_artists, get_artists
from fyyur.schema.artist import ArtistSearchResponse, ArtistWithName
from fyyur.schema.base import SearchSchema
from tests.mock import mock_artist, mock_artists, mock_show


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
        ("1", [ArtistSearchResponse(id=1, name="Artist1", num_upcoming_shows=2)]),
        ("2", [ArtistSearchResponse(id=2, name="Artist2", num_upcoming_shows=1)]),
        ("3", [ArtistSearchResponse(id=3, name="Artist3", num_upcoming_shows=1)]),
        (
            "a",
            [
                ArtistSearchResponse(id=1, name="Artist1", num_upcoming_shows=2),
                ArtistSearchResponse(id=2, name="Artist2", num_upcoming_shows=1),
                ArtistSearchResponse(id=3, name="Artist3", num_upcoming_shows=1),
                ArtistSearchResponse(id=4, name="Artist4", num_upcoming_shows=0),
            ],
        ),
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


def test_find_artists_case_insensitive(app):
    with app.app_context():
        db.session.add(mock_artist(id=10, name="King"))
        db.session.commit()
        find_artists(SearchSchema(search_term="k")) == ArtistSearchResponse(
            id=10, name="King", num_upcoming_shows=0
        )
        find_artists(SearchSchema(search_term="K")) == ArtistSearchResponse(
            id=10, name="King", num_upcoming_shows=0
        )
        find_artists(SearchSchema(search_term="IN")) == ArtistSearchResponse(
            id=10, name="King", num_upcoming_shows=0
        )


def test_find_artists_with_past_shows(app):
    with app.app_context():
        db.session.add(mock_artist(id=10, name="King"))
        db.session.add(mock_show(id=10, venue_id=1, artist_id=1, day_offset=-10))
        db.session.add(mock_show(id=10, venue_id=1, artist_id=1, day_offset=10))
        db.session.commit()
        find_artists(SearchSchema(search_term="King")) == ArtistSearchResponse(
            id=10, name="King", num_upcoming_shows=1
        )
