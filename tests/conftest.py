import pytest

from fyyur import create_app
from fyyur.config import TestingConfig
from fyyur.model import db


@pytest.fixture()
def test_app():
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(test_app):
    return test_app.test_client()
