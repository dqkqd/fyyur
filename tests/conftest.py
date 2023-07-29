import os

import pytest

from fyyur import create_app
from fyyur.config import TestingConfig
from fyyur.model import db
from tests.mock import mock_artists, mock_shows, mock_venues


@pytest.fixture()
def app():
    test_app = create_app(TestingConfig)
    os.remove(test_app.config["TEST_DB_PATH"])

    with test_app.app_context():
        db.create_all()

        for venue in mock_venues():
            db.session.add(venue)
        for artist in mock_artists():
            db.session.add(artist)
        for show in mock_shows():
            db.session.add(show)
        db.session.commit()

    yield test_app

    with test_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
