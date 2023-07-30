from typing import Any

import pytest

from fyyur.models import db
from fyyur.models.artist import Artist
from fyyur.models.show import Show
from fyyur.routes.artist import find_artists, get_artist_info, get_artists
from fyyur.schema.artist import (
    ArtistBase,
    ArtistInfoResponse,
    ArtistSearchResponse,
)
from fyyur.schema.base import SearchSchema
from fyyur.schema.genre import GenreEnum
from fyyur.schema.show import ShowInArtistInfo
from tests.mock import date_future, mock_artist, mock_artists_db, mock_genre, mock_show


def test_get_artists(app):
    with app.app_context():
        artists = [ArtistBase.model_validate(artist) for artist in mock_artists_db()]
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
        db.session.add(mock_artist(id=10, name="King").to_orm(Artist))
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
        db.session.add(mock_artist(id=10, name="King").to_orm(Artist))
        db.session.add(mock_show(venue_id=1, artist_id=1, day_offset=-10).to_orm(Show))
        db.session.add(mock_show(venue_id=1, artist_id=1, day_offset=10).to_orm(Show))
        db.session.commit()
        find_artists(SearchSchema(search_term="King")) == ArtistSearchResponse(
            id=10, name="King", num_upcoming_shows=1
        )


@pytest.mark.parametrize(
    "artist_id, genres",
    [
        (
            1,
            [
                mock_genre(1, GenreEnum.Blues),
                mock_genre(2, GenreEnum.HipHop),
                mock_genre(3, GenreEnum.Jazz),
            ],
        ),
        (
            2,
            [
                mock_genre(3, GenreEnum.Jazz),
                mock_genre(4, GenreEnum.RockNRoll),
                mock_genre(5, GenreEnum.Pop),
            ],
        ),
        (3, [mock_genre(5, GenreEnum.Pop)]),
        (4, []),
    ],
)
def test_get_artist_info(app, artist_id: int, genres: list[GenreEnum]):
    artist = mock_artist(id=artist_id, seeking_venue=True)
    with app.app_context():
        upcoming_shows = (
            Show.query.filter_by(artist_id=artist_id)
            .filter(Show.start_time >= date_future(days=0))
            .all()
        )
        past_shows = (
            Show.query.filter_by(artist_id=artist_id)
            .filter(Show.start_time < date_future(days=0))
            .all()
        )
        expected_artist_info = ArtistInfoResponse(
            **artist.model_dump(exclude=["shows", "genres"]),
            genres=genres,
            past_shows=list(map(ShowInArtistInfo.from_show, past_shows)),
            upcoming_shows=list(map(ShowInArtistInfo.from_show, upcoming_shows)),
            past_shows_count=len(past_shows),
            upcoming_shows_count=len(upcoming_shows),
        )

        artist_info = get_artist_info(artist_id=artist_id)
        assert expected_artist_info == artist_info


def test_show_artist(client):
    response = client.get("artists/1")
    assert response.status_code == 200

    response = client.get("artists/100")
    assert response.status_code == 404


def test_insert_artist(client):
    # artist = mock_artist(id=10, seeking_venue=True)
    # artist.genres = [mock_genre(None, genre=GenreEnum.Country)]
    # print(artist.model_dump_json())
    # response = client.post("/artists/create", data=artist_in_form.model_dump())
    # print(response.status_code)
    # assert False
    pass
