from typing import Any

import pytest
from flask import Flask
from flask.testing import FlaskClient

from fyyur.models import Artist, Genre, Show, db
from fyyur.routes.artist import find_artists, get_artist_info, get_artists
from fyyur.schema.artist import ArtistInfoResponse
from fyyur.schema.base import SearchSchema
from fyyur.schema.genre import GenreEnum
from tests.mock import mock_artist, mock_show
from tests.utils import date_future, date_past


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
    "artist_id, expected_artist_data",
    [
        (
            1,
            {
                "id": 1,
                "name": "Artist1",
                "genres": ["Blues", "Hip-Hop", "Jazz"],
                "city": "San Francisco",
                "state": "CA",
                "phone": "326-123-5000",
                "image_link": "https://images.artist1.com/",
                "website_link": "https://artist1.com/",
                "facebook_link": "https://www.facebook.com/artist1/",
                "seeking_venue": True,
                "seeking_description": "Artist1 Looking for shows",
                "past_shows": [],
                "upcoming_shows": [
                    {
                        "venue_id": 1,
                        "venue_name": "Venue1",
                        "venue_image_link": "https://images.venue1.com/",
                        "start_time": date_future(1),
                    },
                    {
                        "venue_id": 1,
                        "venue_name": "Venue1",
                        "venue_image_link": "https://images.venue1.com/",
                        "start_time": date_future(2),
                    },
                ],
                "past_shows_count": 0,
                "upcoming_shows_count": 2,
            },
        ),
        (
            2,
            {
                "id": 2,
                "name": "Artist2",
                "genres": ["Jazz", "Rock n Roll", "Pop"],
                "city": "San Francisco",
                "state": "CA",
                "phone": "326-123-5000",
                "image_link": "https://images.artist2.com/",
                "website_link": "https://artist2.com/",
                "facebook_link": "https://www.facebook.com/artist2/",
                "seeking_venue": True,
                "seeking_description": "Artist2 Looking for shows",
                "past_shows": [],
                "upcoming_shows": [
                    {
                        "venue_id": 2,
                        "venue_name": "Venue2",
                        "venue_image_link": "https://images.venue2.com/",
                        "start_time": date_future(3),
                    }
                ],
                "past_shows_count": 0,
                "upcoming_shows_count": 1,
            },
        ),
        (
            3,
            {
                "id": 3,
                "name": "Artist3",
                "genres": ["Pop"],
                "city": "San Francisco",
                "state": "CA",
                "phone": "326-123-5000",
                "image_link": "https://images.artist3.com/",
                "website_link": "https://artist3.com/",
                "facebook_link": "https://www.facebook.com/artist3/",
                "seeking_venue": True,
                "seeking_description": "Artist3 Looking for shows",
                "past_shows": [],
                "upcoming_shows": [
                    {
                        "venue_id": 1,
                        "venue_name": "Venue1",
                        "venue_image_link": "https://images.venue1.com/",
                        "start_time": date_future(4),
                    }
                ],
                "past_shows_count": 0,
                "upcoming_shows_count": 1,
            },
        ),
        (
            4,
            {
                "id": 4,
                "name": "Artist4",
                "genres": [],
                "city": "San Francisco",
                "state": "CA",
                "phone": "326-123-5000",
                "image_link": "https://images.artist4.com/",
                "website_link": "https://artist4.com/",
                "facebook_link": "https://www.facebook.com/artist4/",
                "seeking_venue": True,
                "seeking_description": "Artist4 Looking for shows",
                "past_shows": [
                    {
                        "venue_id": 2,
                        "venue_name": "Venue2",
                        "venue_image_link": "https://images.venue2.com/",
                        "start_time": date_past(4),
                    }
                ],
                "upcoming_shows": [],
                "past_shows_count": 1,
                "upcoming_shows_count": 0,
            },
        ),
    ],
)
def test_get_artist_info(
    app: Flask, artist_id: int, expected_artist_data: dict[str, Any]
) -> None:
    with app.app_context():
        artist_info_response = get_artist_info(artist_id=artist_id)
        assert artist_info_response is not None
        assert expected_artist_data == artist_info_response.model_dump()
        assert (
            ArtistInfoResponse.model_validate(expected_artist_data)
            == artist_info_response
        )


def test_show_artist(client: FlaskClient) -> None:
    response = client.get("artists/1")
    assert response.status_code == 200

    response = client.get("artists/100")
    assert response.status_code == 404


def test_basic_insert_artist(app: Flask, client: FlaskClient) -> None:
    artist = mock_artist(id=10, name="King", seeking_venue=True)
    artist_in_form = artist.to_orm(Artist).artist_in_form
    artist_in_form.genres = [GenreEnum.Blues, GenreEnum.Pop]
    response = client.post("/artists/create", data=artist_in_form.model_dump())
    assert response.status_code == 200

    with app.app_context():
        artists: list[Artist] = Artist.query.filter_by(name="King").all()
        assert len(artists) == 1
        assert artists[0].artist_in_form == artist_in_form


def test_insert_artist_should_insert_genre(app: Flask, client: FlaskClient) -> None:
    artist = mock_artist(id=10, name="King", seeking_venue=True)
    artist_in_form = artist.to_orm(Artist).artist_in_form
    artist_in_form.genres = [GenreEnum.Folk]

    # make sure Folk doesn't exist
    with app.app_context():
        assert Genre.query.filter_by(name=GenreEnum.Folk.value).first() is None

    response = client.post("/artists/create", data=artist_in_form.model_dump())
    assert response.status_code == 200

    with app.app_context():
        assert Genre.query.filter_by(name=GenreEnum.Folk.value).first() is not None


def test_insert_artist_should_not_insert_duplicated_genres(
    app: Flask, client: FlaskClient
) -> None:
    artist = mock_artist(id=10, name="King", seeking_venue=True)
    artist_in_form = artist.to_orm(Artist).artist_in_form
    artist_in_form.genres = [GenreEnum.Folk]
    response = client.post("/artists/create", data=artist_in_form.model_dump())
    assert response.status_code == 200

    with app.app_context():
        king: Artist = Artist.query.filter_by(name="King").first()
        assert len(king.genres) == 1
        assert king.genres[0].name == GenreEnum.Folk.value
        assert Genre.query.filter_by(name=GenreEnum.Folk.value).count() == 1

    artist = mock_artist(id=20, name="Queen", seeking_venue=True)
    artist_in_form = artist.to_orm(Artist).artist_in_form
    artist_in_form.genres = [GenreEnum.Folk]
    response = client.post("/artists/create", data=artist_in_form.model_dump())
    assert response.status_code == 200

    with app.app_context():
        queen: Artist = Artist.query.filter_by(name="Queen").first()
        assert len(queen.genres) == 1
        assert queen.genres[0].name == GenreEnum.Folk.value
        assert Genre.query.filter_by(name=GenreEnum.Folk.value).count() == 1


def test_artist_edit_form_request(client: FlaskClient) -> None:
    response = client.get("/artists/1/edit")
    assert response.status_code == 200

    response = client.get("/artists/100/edit")
    assert response.status_code == 404


def test_update_artist_basic(app: Flask, client: FlaskClient) -> None:
    with app.app_context():
        artist: Artist | None = Artist.query.filter_by(id=1).first()
        assert artist is not None

        # Fold doesn't exist
        for genre in artist.genres:
            assert genre.name != GenreEnum.Folk.value

        artist_in_form = artist.artist_in_form

        new_genres = [GenreEnum.Folk]
        assert artist_in_form.genres != new_genres
        artist_in_form.genres = new_genres

    client.post("/artists/1/edit", data=artist_in_form.model_dump(mode="json"))

    with app.app_context():
        updated_artist: Artist | None = Artist.query.filter_by(id=1).first()
        assert updated_artist is not None

        # Folk exist now
        assert len(updated_artist.genres) == 1
        assert updated_artist.genres[0].name == GenreEnum.Folk.value


def test_update_non_existing_artist(app: Flask, client: FlaskClient) -> None:
    with app.app_context():
        artist: Artist | None = Artist.query.filter_by(id=1).first()
        assert artist is not None
        artist_in_form = artist.artist_in_form
        artist_in_form.name = "King"

    client.post("/artists/100/edit", data=artist_in_form.model_dump(mode="json"))

    with app.app_context():
        assert Artist.query.filter_by(id=100).first() is None
        updated_artist: Artist | None = Artist.query.filter_by(id=1).first()
        assert updated_artist is not None
        assert updated_artist.artist_in_form != artist_in_form
