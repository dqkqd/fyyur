import sqlalchemy as sa

from fyyur.models import db


class Genre(db.Model):
    __tablename__ = "Genre"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
