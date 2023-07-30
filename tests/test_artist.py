from typing import Any

import pytest
from flask import Flask
from flask.testing import FlaskClient

from fyyur.models import Artist, Show, db
from fyyur.routes.artist import find_artists, get_artist_info, get_artists
from fyyur.schema.base import SearchSchema
from fyyur.schema.genre import GenreEnum
from tests.mock import mock_artist, mock_genre, mock_show
from tests.utils import date_past


def test_get_artists(app: Flask) -> None:
    expected_artists_data = [
        {"id": 1, "name": "Artist1"},
        {"id": 2, "name": "Artist2"},
        {"id": 3, "name": "Artist3"},
        {"id": 4, "name": "Artist4"},
    ]

    with app.app_context():
        artists = get_artists()
        artists_data = [artist.model_dump() for artist in artists]
        assert expected_artists_data == artists_data


def test_get_aritsts_status_200(client: FlaskClient) -> None:
    assert client.get("/artists/").status_code == 200


@pytest.mark.parametrize(
    "search_term, expected_artists_data",
    [
        ("1", [{"id": 1, "name": "Artist1", "num_upcoming_shows": 2}]),
        ("2", [{"id": 2, "name": "Artist2", "num_upcoming_shows": 1}]),
        ("3", [{"id": 3, "name": "Artist3", "num_upcoming_shows": 1}]),
        (
            "a",
            [
                {"id": 1, "name": "Artist1", "num_upcoming_shows": 2},
                {"id": 2, "name": "Artist2", "num_upcoming_shows": 1},
                {"id": 3, "name": "Artist3", "num_upcoming_shows": 1},
                {"id": 4, "name": "Artist4", "num_upcoming_shows": 0},
            ],
        ),
    ],
)
def test_basic_find_artists(
    app: Flask,
    client: FlaskClient,
    search_term: str,
    expected_artists_data: list[dict[str, Any]],
) -> None:
    search_schema = SearchSchema(search_term=search_term)
    with app.app_context():
        artists = find_artists(search_schema)
        artists_data = [artist.model_dump() for artist in artists]
    assert artists_data == expected_artists_data

    response = client.post("/artists/search", data=search_schema.model_dump())
    assert response.status_code == 200


def test_find_artists_case_insensitive(app: Flask) -> None:
    with app.app_context():
        db.session.add(mock_artist(id=10, name="King").to_orm(Artist))
        db.session.commit()

        for search_term in ["k", "K", "IN"]:
            artists = find_artists(SearchSchema(search_term=search_term))
            artists_data = [artist.model_dump() for artist in artists]
            assert artists_data == [{"id": 10, "name": "King", "num_upcoming_shows": 0}]


def test_find_artists_with_past_shows(app: Flask) -> None:
    with app.app_context():
        db.session.add(mock_artist(id=10, name="King").to_orm(Artist))
        db.session.add(mock_show(venue_id=1, artist_id=10, day_offset=-10).to_orm(Show))
        db.session.add(mock_show(venue_id=1, artist_id=10, day_offset=10).to_orm(Show))
        db.session.commit()
        artists = find_artists(SearchSchema(search_term="King"))
        artists_data = [artist.model_dump() for artist in artists]
        assert artists_data == [{"id": 10, "name": "King", "num_upcoming_shows": 1}]


@pytest.mark.parametrize(
    "artist_id, genres",
    [
        (1, [GenreEnum.Blues, GenreEnum.HipHop, GenreEnum.Jazz]),
        (2, [GenreEnum.Jazz, GenreEnum.RockNRoll, GenreEnum.Pop]),
        (3, [GenreEnum.Pop]),
        (4, []),
    ],
)
def test_get_artist_info(app: Flask, artist_id: int, genres: list[GenreEnum]) -> None:
    artist = mock_artist(id=artist_id, seeking_venue=True)
    with app.app_context():
        upcoming_shows: list[Show] = (
            Show.query.filter_by(artist_id=artist_id)
            .filter(Show.start_time >= date_future(days=0))
            .all()
        )
        past_shows: list[Show] = (
            Show.query.filter_by(artist_id=artist_id)
            .filter(Show.start_time < date_future(days=0))
            .all()
        )
        expected_artist_info_response = artist.to_orm(
            Artist
        ).artist_info_response.model_copy(
            update=dict(
                genres=genres,
                past_shows=[show.show_in_artist_info for show in past_shows],
                upcoming_shows=[show.show_in_artist_info for show in upcoming_shows],
                past_shows_count=len(past_shows),
                upcoming_shows_count=len(upcoming_shows),
            ),
        )

        artist_info_response = get_artist_info(artist_id=artist_id)
        assert expected_artist_info_response == artist_info_response


def test_show_artist(client: FlaskClient) -> None:
    response = client.get("artists/1")
    assert response.status_code == 200

    response = client.get("artists/100")
    assert response.status_code == 404


def test_insert_artist(client: FlaskClient) -> None:
    artist = mock_artist(id=10, seeking_venue=True)
    artist.genres = [mock_genre(None, genre=GenreEnum.Country)]
    # print(artist.model_dump_json())
    # response = client.post("/artists/create", data=artist_in_form.model_dump())
    # print(response.status_code)
    # assert False
    pass
