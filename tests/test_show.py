from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient

from fyyur.models import Artist, Show, Venue, db
from fyyur.routes.show import get_shows
from fyyur.schema.show import ShowResponse
from tests.mock import mock_artist, mock_show, mock_venue
from tests.utils import date_future


def test_get_shows_status_200(client: FlaskClient) -> None:
    response = client.get("/shows/")
    assert response.status_code == 200
    assert b"Venue1" in response.data
    assert b"Artist1" in response.data


def add_show(
    app: Flask, client: FlaskClient, venue_id: int, artist_id: int, day_offset: int
) -> bool:
    show = mock_show(venue_id=venue_id, artist_id=artist_id, day_offset=day_offset)

    prior_existed: bool = False
    existed: bool = False
    with app.app_context():
        prior_existed = (
            Show.query.filter_by(
                venue_id=show.venue_id,
                artist_id=show.artist_id,
                start_time=show.start_time,
            ).first()
            is not None
        )

        client.post("/shows/create", data=show.model_dump())

        existed = (
            Show.query.filter_by(
                venue_id=show.venue_id,
                artist_id=show.artist_id,
                start_time=show.start_time,
            ).first()
            is not None
        )

    inserted = not prior_existed and existed
    return inserted


def test_create_show_successful(app: Flask, client: FlaskClient) -> None:
    with app.app_context():
        venue = mock_venue(100).to_orm(Venue)
        artist = mock_artist(200).to_orm(Artist)
        db.session.add(venue)
        db.session.add(artist)
        db.session.commit()

    # inserted into database
    assert add_show(app=app, client=client, venue_id=100, artist_id=200, day_offset=100)


def test_get_shows(app: Flask, client: FlaskClient) -> None:
    assert add_show(app=app, client=client, venue_id=1, artist_id=1, day_offset=100)
    assert add_show(app=app, client=client, venue_id=1, artist_id=2, day_offset=200)

    expected_shows: list[dict[str, int | str | datetime]] = [
        {
            "venue_id": 1,
            "venue_name": "Venue1",
            "artist_id": 1,
            "artist_name": "Artist1",
            "artist_image_link": "https://images.artist1.com/",
            "start_time": date_future(100),
        },
        {
            "venue_id": 1,
            "venue_name": "Venue1",
            "artist_id": 2,
            "artist_name": "Artist2",
            "artist_image_link": "https://images.artist2.com/",
            "start_time": date_future(200),
        },
    ]

    with app.app_context():
        all_shows = get_shows()
        dumped_shows = [show.model_dump() for show in get_shows()]
        for expected_show in expected_shows:
            assert ShowResponse.model_validate(expected_show) in all_shows
            assert expected_show in dumped_shows


@pytest.mark.parametrize("venue_id, artist_id", [(1, 100), (100, 1), (100, 100)])
def test_create_show_venue_or_artist_doesnt_exist(
    app: Flask, client: FlaskClient, venue_id: int, artist_id: int
) -> None:
    assert not add_show(
        app=app, client=client, venue_id=venue_id, artist_id=artist_id, day_offset=100
    )


def test_create_show_duplicated(app: Flask, client: FlaskClient) -> None:
    assert add_show(app=app, client=client, venue_id=1, artist_id=1, day_offset=100)
    assert not add_show(app=app, client=client, venue_id=1, artist_id=1, day_offset=100)


def test_create_show_same_date_same_venue(app: Flask, client: FlaskClient) -> None:
    assert add_show(app=app, client=client, venue_id=1, artist_id=1, day_offset=100)
    assert not add_show(app=app, client=client, venue_id=1, artist_id=2, day_offset=100)


def test_create_show_same_date_same_artist(app: Flask, client: FlaskClient) -> None:
    assert add_show(app=app, client=client, venue_id=1, artist_id=1, day_offset=100)
    assert not add_show(app=app, client=client, venue_id=2, artist_id=1, day_offset=100)


def test_create_show_same_date_different_venue_and_artist(
    app: Flask, client: FlaskClient
) -> None:
    assert add_show(app=app, client=client, venue_id=1, artist_id=1, day_offset=100)
    assert add_show(app=app, client=client, venue_id=2, artist_id=2, day_offset=100)


def test_create_show_in_the_past(app: Flask, client: FlaskClient) -> None:
    assert not add_show(app=app, client=client, venue_id=2, artist_id=2, day_offset=-100)
