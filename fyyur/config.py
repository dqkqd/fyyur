import os
from pathlib import Path


class Config(object):
    SECRET_KEY = os.urandom(32)
    # Grabs the folder where the script runs.
    basedir = os.path.abspath(os.path.dirname(__file__))


class NormalConfig(Config):
    # Enable debug mode.
    DEBUG = True

    # Connect to the database

    SQLALCHEMY_DATABASE_URI = "postgresql://postgres@localhost:5432/fyyur"


class TestingConfig(Config):
    TESTING = True
    TEST_DB_PATH = Path(__file__).parent.parent / "tests" / "test.db"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(TEST_DB_PATH)
    WTF_CSRF_ENABLED = False
