import pytest

from fyyur import create_app
from fyyur.config import TestingConfig
from fyyur.model import db


@pytest.fixture()
def app():
    test_app = create_app(TestingConfig)

    with test_app.app_context():
        db.create_all()

    yield test_app

    with test_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
