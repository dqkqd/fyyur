import os
from typing import Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from fyyur import create_app
from fyyur.config import TestingConfig
from fyyur.models import db
from tests.mock import insert_mock_data


@pytest.fixture()
def app() -> Iterator[Flask]:
    test_app = create_app(TestingConfig)

    test_db_path = test_app.config["TEST_DB_PATH"]
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    with test_app.app_context():
        db.create_all()
        insert_mock_data()
        db.session.commit()

    yield test_app

    with test_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()
