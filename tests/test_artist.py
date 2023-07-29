from fyyur.model import db
from fyyur.routes.artist import get_artists
from fyyur.schema.artist import ArtistInDb


def test_get_artists(test_app):
    with test_app.app_context():
        artists = get_artists()
        assert not artists, "No artist's existed in database yet"

        artists_json = [
            {"id": 1, "name": "Artist1"},
            {"id": 2, "name": "Artist2"},
            {"id": 3, "name": "Artist3"},
            {"id": 4, "name": "Artist4"},
        ]

        for artist_json in artists_json:
            artist = ArtistInDb(**artist_json).to_orm()
            db.session.add(artist)
        db.session.commit()

        artists = get_artists()
        assert artists == artists_json
