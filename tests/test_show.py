import datetime

import pytest

from fyyur.model import Artist, Show, Venue, db
from fyyur.routes.show import get_shows
from fyyur.schema.artist import ArtistSchema
from fyyur.schema.show import ShowSchema
from fyyur.schema.venue import VenueSchema


@pytest.fixture(autouse=True, scope="function")
def mock_test_show_data(test_app):
    venue1 = VenueSchema(id=1, name="Venue1").to_orm(Venue)

    artist1 = ArtistSchema(
        id=1, name="Artist1", image_link="https://example1.com"
    ).to_orm(Artist)

    artist2 = ArtistSchema(
        id=2, name="Artist2", image_link="https://example2.com"
    ).to_orm(Artist)

    show1 = ShowSchema(
        id=1,
        venue_id=venue1.id,
        artist_id=artist1.id,
        start_time="2019-05-21T21:30:00.000Z",
    ).to_orm(Show)

    show2 = ShowSchema(
        id=2,
        venue_id=venue1.id,
        artist_id=artist2.id,
        start_time="2019-05-22T21:30:00.000Z",
    ).to_orm(Show)

    venue1.shows = [show1, show2]
    artist1.shows = [show1]
    artist2.shows = [show2]

    with test_app.app_context():
        db.session.add(venue1)
        db.session.add(artist1)
        db.session.add(artist2)
        db.session.commit()


def test_get_shows_status_200(client):
    response = client.get("/shows/")
    assert response.status_code == 200
    assert b"Venue1" in response.data
    assert b"Artist1" in response.data


def test_get_shows(test_app):
    expected_shows = [
        {
            "venue_id": 1,
            "venue_name": "Venue1",
            "artist_id": 1,
            "artist_name": "Artist1",
            "artist_image_link": "https://example1.com/",
            "start_time": "2019-05-21T21:30:00",
        },
        {
            "venue_id": 1,
            "venue_name": "Venue1",
            "artist_id": 2,
            "artist_name": "Artist2",
            "artist_image_link": "https://example2.com/",
            "start_time": "2019-05-22T21:30:00",
        },
    ]

    with test_app.app_context():
        assert expected_shows == get_shows()


@pytest.mark.parametrize("venue_id, artist_id", [(1, 100), (100, 1), (100, 100)])
def test_create_show_invalid(test_app, client, venue_id: int, artist_id: int):
    response = client.post(
        "/shows/create",
        data={
            "venue_id": venue_id,
            "artist_id": artist_id,
            "start_time": datetime.datetime(2023, 7, 29, 2, 2, 32),
        },
    )

    # redirecting to /shows/create again
    assert response.status_code == 302

    # nothing is inserted into database
    with test_app.app_context():
        assert not Show.query.filter_by(venue_id=venue_id, artist_id=artist_id).all()


def test_create_show_successful(test_app, client):
    with test_app.app_context():
        venue = VenueSchema(id=100).to_orm(Venue)
        artist = ArtistSchema(id=200).to_orm(Artist)
        db.session.add(venue)
        db.session.add(artist)
        db.session.commit()

    # this show hasn't exist in database yet
    with test_app.app_context():
        assert not Show.query.filter_by(venue_id=100, artist_id=200).all()

    response = client.post(
        "/shows/create",
        data={
            "venue_id": 100,
            "artist_id": 200,
            "start_time": datetime.datetime(2023, 7, 29, 2, 2, 32),
        },
    )

    # inserted into database
    assert response.status_code == 200
    with test_app.app_context():
        shows = Show.query.filter_by(venue_id=100, artist_id=200).all()
        assert len(shows) == 1
