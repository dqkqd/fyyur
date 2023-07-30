import os

import pytest

from fyyur import create_app
from fyyur.config import TestingConfig
from fyyur.models import db
from tests.mock import insert_mock_data


@pytest.fixture()
def app():
    test_app = create_app(TestingConfig)
    os.remove(test_app.config["TEST_DB_PATH"])

    with test_app.app_context():
        db.create_all()
        insert_mock_data()
        db.session.commit()

    yield test_app

    with test_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
