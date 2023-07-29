from datetime import datetime, timedelta
from typing import Any

import pytest

from fyyur.constant import DATETIME_FORMAT
from fyyur.model import db
from fyyur.routes.artist import find_artists, get_artists
from fyyur.schema.artist import ArtistInDb, ArtistWithName
from fyyur.schema.base import SearchSchema
from fyyur.schema.show import ShowInDb
from fyyur.schema.venue import VenueInDb


def test_get_artists(app):
    with app.app_context():
        artists = get_artists()
        assert not artists, "No artist's existed in database yet"

        artists_json = [
            {"id": 1, "name": "Artist1"},
            {"id": 2, "name": "Artist2"},
            {"id": 3, "name": "Artist3"},
            {"id": 4, "name": "Artist4"},
        ]

        for artist_json in artists_json:
            artist = ArtistWithName(**artist_json).to_orm()
            db.session.add(artist)
        db.session.commit()

        artists = get_artists()
        assert artists == artists_json


@pytest.mark.parametrize(
    "search_term, expected_result",
    [
        ("b", [{"id": 1, "name": "ab1", "num_upcoming_shows": 1}]),
        ("B", [{"id": 1, "name": "ab1", "num_upcoming_shows": 1}]),
        ("1", [{"id": 1, "name": "ab1", "num_upcoming_shows": 1}]),
        ("2", [{"id": 2, "name": "Ac2", "num_upcoming_shows": 2}]),
        ("3", [{"id": 3, "name": "ad3", "num_upcoming_shows": 0}]),
        ("4", []),
        (
            "a",
            [
                {"id": 1, "name": "ab1", "num_upcoming_shows": 1},
                {"id": 2, "name": "Ac2", "num_upcoming_shows": 2},
                {"id": 3, "name": "ad3", "num_upcoming_shows": 0},
            ],
        ),
        (
            "A",
            [
                {"id": 1, "name": "ab1", "num_upcoming_shows": 1},
                {"id": 2, "name": "Ac2", "num_upcoming_shows": 2},
                {"id": 3, "name": "ad3", "num_upcoming_shows": 0},
            ],
        ),
    ],
)
def test_find_artists(
    app, client, search_term: str, expected_result: list[dict[str, Any]]
):
    with app.app_context():
        venue = VenueInDb(id=1).to_orm()
        artists = [
            ArtistInDb(id=1, name="ab1").to_orm(),
            ArtistInDb(id=2, name="Ac2").to_orm(),
            ArtistInDb(id=3, name="ad3").to_orm(),
        ]
        db.session.add(venue)
        for artist in artists:
            db.session.add(artist)
        db.session.commit()

    shows = [
        ShowInDb(
            venue_id=1,
            artist_id=1,
            start_time=(datetime.now() + timedelta(days=1)).strftime(DATETIME_FORMAT),
        ),
        ShowInDb(
            venue_id=1,
            artist_id=2,
            start_time=(datetime.now() + timedelta(days=3)).strftime(DATETIME_FORMAT),
        ),
        ShowInDb(
            venue_id=1,
            artist_id=2,
            start_time=(datetime.now() + timedelta(days=5)).strftime(DATETIME_FORMAT),
        ),
    ]

    for show in shows:
        response = client.post("/shows/create", data=show.model_dump())
        assert response.status_code == 200

    search_schema = SearchSchema(search_term=search_term)
    with app.app_context():
        artists = find_artists(search_schema)
    assert artists == expected_result

    response = client.post("/artists/search", data=search_schema.model_dump())
    assert response.status_code == 200
