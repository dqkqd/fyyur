import pytest

from fyyur.model import Show, db
from fyyur.routes.show import get_shows
from fyyur.schema.artist import ArtistInDb
from fyyur.schema.show import ShowBase
from fyyur.schema.venue import VenueInDb
from tests.mock import date_future


def test_get_shows_status_200(client):
    response = client.get("/shows/")
    assert response.status_code == 200
    assert b"Venue1" in response.data
    assert b"Artist1" in response.data


# TODO: add more test about how we create show with same venue, same artist
@pytest.mark.parametrize("venue_id, artist_id", [(1, 100), (100, 1), (100, 100)])
def test_create_show_venue_or_artist_doesnt_exist(
    app, client, venue_id: int, artist_id: int
):
    response = client.post(
        "/shows/create",
        data={
            "venue_id": venue_id,
            "artist_id": artist_id,
            "start_time": date_future(days=4),
        },
    )

    # redirecting to /shows/create again
    assert response.status_code == 302

    # nothing is inserted into database
    with app.app_context():
        assert not Show.query.filter_by(venue_id=venue_id, artist_id=artist_id).all()


def test_create_show_successful(app, client):
    with app.app_context():
        venue = VenueInDb(id=100).to_orm()
        artist = ArtistInDb(id=200).to_orm()
        db.session.add(venue)
        db.session.add(artist)
        db.session.commit()

    # this show hasn't exist in database yet
    with app.app_context():
        assert not Show.query.filter_by(venue_id=100, artist_id=200).all()

    show_data = ShowBase(
        venue_id=100,
        artist_id=200,
        start_time=date_future(days=100),
    ).model_dump()

    response = client.post(
        "/shows/create",
        data=show_data,
    )

    # inserted into database
    assert response.status_code == 200
    with app.app_context():
        shows = Show.query.filter_by(venue_id=100, artist_id=200).all()
        assert len(shows) == 1

    # could not insert the same show data again
    response = client.post(
        "/shows/create",
        data=show_data,
    )
    assert response.status_code == 302
    with app.app_context():
        shows = Show.query.filter_by(venue_id=100, artist_id=200).all()
        assert len(shows) == 1


def test_get_shows(app, client):
    show1 = ShowBase(
        venue_id=1,
        artist_id=1,
        start_time=date_future(days=100),
    )

    show2 = ShowBase(
        venue_id=1,
        artist_id=2,
        start_time=date_future(days=200),
    )

    for show in [show1, show2]:
        client.post(
            "/shows/create",
            data=show.model_dump(),
        )

    expected_shows = [
        {
            **show1.model_dump(mode="json"),
            "venue_name": "Venue1",
            "artist_name": "Artist1",
            "artist_image_link": "https://example1.com/",
        },
        {
            **show2.model_dump(mode="json"),
            "venue_name": "Venue1",
            "artist_name": "Artist2",
            "artist_image_link": "https://example2.com/",
        },
    ]

    with app.app_context():
        all_shows = get_shows()
        for show in expected_shows:
            assert show in all_shows
