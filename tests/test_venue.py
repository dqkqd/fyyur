from flask import Flask

from fyyur.models import Venue, db
from fyyur.routes.venue import get_venues
from fyyur.schema.base import State
from tests.mock import mock_venue


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
