from typing import Any

import pytest
from flask import Flask
from flask.testing import FlaskClient

from fyyur.models import Show, Venue, db
from fyyur.routes.venue import find_venues, get_venues
from fyyur.schema.base import SearchSchema, State
from fyyur.schema.genre import GenreEnum
from tests.mock import mock_show, mock_venue


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
