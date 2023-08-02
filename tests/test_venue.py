from typing import Any

import pytest
from flask import Flask
from flask.testing import FlaskClient

from fyyur.models import Show, Venue, db
from fyyur.routes.venue import find_venues, get_venue_info, get_venues
from fyyur.schema.base import SearchSchema, State
from fyyur.schema.genre import GenreEnum
from fyyur.schema.venue import VenueInfoResponse
from tests.mock import mock_show, mock_venue
from tests.utils import date_future, date_past


def test_get_venues(app: Flask) -> None:
    with app.app_context():
        venue1 = mock_venue(id=10, city="test1", state=State.NY)
        venue2 = mock_venue(id=11, city="test2", state=State.NY)
        db.session.add_all([venue1.to_orm(Venue), venue2.to_orm(Venue)])
        db.session.commit()

    expected_venues_data = [
        {
            "city": "San Francisco",
            "state": "CA",
            "venues": [
                {"name": "Venue1", "id": 1, "num_upcoming_shows": 3},
                {"name": "Venue2", "id": 2, "num_upcoming_shows": 1},
                {"name": "Venue3", "id": 3, "num_upcoming_shows": 0},
            ],
        },
        {
            "city": "test1",
            "state": "NY",
            "venues": [
                {"name": "Venue10", "id": 10, "num_upcoming_shows": 0},
            ],
        },
        {
            "city": "test2",
            "state": "NY",
            "venues": [
                {"name": "Venue11", "id": 11, "num_upcoming_shows": 0},
            ],
        },
    ]

    with app.app_context():
        venues = get_venues()
        venues_data = [venue.model_dump() for venue in venues]
        assert expected_venues_data == venues_data


def test_basic_insert_venue(app: Flask, client: FlaskClient) -> None:
    venue = mock_venue(id=10, name="King Venue")
    venue_in_form = venue.to_orm(Venue).venue_in_form
    venue_in_form.genres = [GenreEnum.Blues, GenreEnum.Pop]
    if not venue_in_form.seeking_talent:
        data = venue_in_form.model_dump(exclude={"seeking_talent"})
    else:
        data = venue_in_form.model_dump()
    response = client.post("/venues/create", json=data)
    assert response.status_code == 200

    with app.app_context():
        venues: list[Venue] = Venue.query.filter_by(name="King Venue").all()
        assert len(venues) == 1
        assert venues[0].venue_in_form == venue_in_form


@pytest.mark.parametrize(
    "search_term, expected_venues_data",
    [
        ("1", [{"id": 1, "name": "Venue1", "num_upcoming_shows": 3}]),
        ("2", [{"id": 2, "name": "Venue2", "num_upcoming_shows": 1}]),
        ("3", [{"id": 3, "name": "Venue3", "num_upcoming_shows": 0}]),
        (
            "v",
            [
                {"id": 1, "name": "Venue1", "num_upcoming_shows": 3},
                {"id": 2, "name": "Venue2", "num_upcoming_shows": 1},
                {"id": 3, "name": "Venue3", "num_upcoming_shows": 0},
            ],
        ),
    ],
)
def test_basic_find_venues(
    app: Flask,
    client: FlaskClient,
    search_term: str,
    expected_venues_data: list[dict[str, Any]],
) -> None:
    search_schema = SearchSchema(search_term=search_term)
    with app.app_context():
        venues = find_venues(search_schema)
        venues_data = [venue.model_dump() for venue in venues]
    assert venues_data == expected_venues_data

    response = client.post("/venues/search", data=search_schema.model_dump())
    assert response.status_code == 200


def test_find_venues_case_insensitive(app: Flask) -> None:
    with app.app_context():
        db.session.add(mock_venue(id=10, name="King").to_orm(Venue))
        db.session.commit()

        for search_term in ["k", "K", "IN"]:
            venues = find_venues(SearchSchema(search_term=search_term))
            venues_data = [venue.model_dump() for venue in venues]
            assert venues_data == [{"id": 10, "name": "King", "num_upcoming_shows": 0}]


def test_find_venues_with_past_shows(app: Flask) -> None:
    with app.app_context():
        db.session.add(mock_venue(id=10, name="King").to_orm(Venue))
        db.session.add(mock_show(venue_id=10, artist_id=1, day_offset=-100).to_orm(Show))
        db.session.add(mock_show(venue_id=10, artist_id=1, day_offset=100).to_orm(Show))
        db.session.commit()

        venues = find_venues(SearchSchema(search_term="King"))
        venues_data = [venue.model_dump() for venue in venues]
        assert venues_data == [{"id": 10, "name": "King", "num_upcoming_shows": 1}]


@pytest.mark.parametrize(
    "venue_id, expected_venue_data",
    [
        (
            1,
            {
                "id": 1,
                "name": "Venue1",
                "genres": ["Blues", "Hip-Hop", "Jazz"],
                "address": "123",
                "city": "San Francisco",
                "state": "CA",
                "phone": "326-123-5000",
                "image_link": "https://images.venue1.com/",
                "website_link": "https://venue1.com/",
                "facebook_link": "https://www.facebook.com/venue1/",
                "seeking_talent": True,
                "seeking_description": "Venue1: looking for artist.",
                "past_shows": [],
                "upcoming_shows": [
                    {
                        "artist_id": 1,
                        "artist_name": "Artist1",
                        "artist_image_link": "https://images.artist1.com/",
                        "start_time": date_future(1),
                    },
                    {
                        "artist_id": 1,
                        "artist_name": "Artist1",
                        "artist_image_link": "https://images.artist1.com/",
                        "start_time": date_future(2),
                    },
                    {
                        "artist_id": 3,
                        "artist_name": "Artist3",
                        "artist_image_link": "https://images.artist3.com/",
                        "start_time": date_future(4),
                    },
                ],
                "past_shows_count": 0,
                "upcoming_shows_count": 3,
            },
        ),
        (
            2,
            {
                "id": 2,
                "name": "Venue2",
                "genres": ["Jazz", "Rock n Roll", "Pop"],
                "address": "123",
                "city": "San Francisco",
                "state": "CA",
                "phone": "326-123-5000",
                "image_link": "https://images.venue2.com/",
                "website_link": "https://venue2.com/",
                "facebook_link": "https://www.facebook.com/venue2/",
                "seeking_talent": True,
                "seeking_description": "Venue2: looking for artist.",
                "past_shows": [
                    {
                        "artist_id": 4,
                        "artist_name": "Artist4",
                        "artist_image_link": "https://images.artist4.com/",
                        "start_time": date_past(4),
                    },
                ],
                "upcoming_shows": [
                    {
                        "artist_id": 2,
                        "artist_name": "Artist2",
                        "artist_image_link": "https://images.artist2.com/",
                        "start_time": date_future(3),
                    },
                ],
                "past_shows_count": 1,
                "upcoming_shows_count": 1,
            },
        ),
        (
            3,
            {
                "id": 3,
                "name": "Venue3",
                "genres": ["Pop"],
                "address": "123",
                "city": "San Francisco",
                "state": "CA",
                "phone": "326-123-5000",
                "image_link": "https://images.venue3.com/",
                "website_link": "https://venue3.com/",
                "facebook_link": "https://www.facebook.com/venue3/",
                "seeking_talent": True,
                "seeking_description": "Venue3: looking for artist.",
                "past_shows": [],
                "upcoming_shows": [],
                "past_shows_count": 0,
                "upcoming_shows_count": 0,
            },
        ),
        (100, None),
    ],
)
def test_get_venue_info(
    app: Flask, venue_id: int, expected_venue_data: dict[str, Any] | None
) -> None:
    with app.app_context():
        venue_info_response = get_venue_info(venue_id=venue_id)
        if expected_venue_data is not None:
            assert isinstance(venue_info_response, VenueInfoResponse)
            assert expected_venue_data == venue_info_response.model_dump()
            assert (
                VenueInfoResponse.model_validate(expected_venue_data)
                == venue_info_response
            )
        else:
            assert venue_info_response is None


def test_update_venue_basic(app: Flask, client: FlaskClient) -> None:
    with app.app_context():
        venue: Venue | None = Venue.query.filter_by(id=1).first()
        assert venue is not None

        # Folk doesn't exist
        for genre in venue.genres:
            assert genre.name != GenreEnum.Folk.value

        venue_in_form = venue.venue_in_form

        new_genres = [GenreEnum.Folk]
        assert venue_in_form.genres != new_genres
        venue_in_form.genres = new_genres

    client.post("/venues/1/edit", data=venue_in_form.model_dump(mode="json"))

    with app.app_context():
        updated_venue: Venue | None = venue.query.filter_by(id=1).first()
        assert updated_venue is not None

        # Folk exist now
        assert len(updated_venue.genres) == 1
        assert updated_venue.genres[0].name == GenreEnum.Folk.value


def test_update_non_existing_venue(app: Flask, client: FlaskClient) -> None:
    with app.app_context():
        venue: Venue | None = Venue.query.filter_by(id=1).first()
        assert venue is not None
        venue_in_form = venue.venue_in_form
        venue_in_form.name = "King"

    client.post("/venues/100/edit", data=venue_in_form.model_dump(mode="json"))

    with app.app_context():
        assert venue.query.filter_by(id=100).first() is None
        updated_venue: Venue | None = venue.query.filter_by(id=1).first()
        assert updated_venue is not None
        assert updated_venue.venue_in_form != venue_in_form


def test_delete_venue(app: Flask, client: FlaskClient) -> None:
    with app.app_context():
        assert Venue.query.filter_by(id=1).first() is not None
        client.delete("/venues/1")
        assert Venue.query.filter_by(id=1).first() is None


def test_edit_venue_request(client: FlaskClient) -> None:
    response = client.get("/venues/1/edit")
    assert response.status_code == 200

    response = client.get("/venues/100/edit")
    assert response.status_code == 404
