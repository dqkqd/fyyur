from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from fyyur.models import db
from fyyur.models.reference import artist_genre, venue_genre

if TYPE_CHECKING:
    from fyyur.models.artist import Artist
    from fyyur.models.venue import Venue


class Genre(db.Model):
    __tablename__ = "Genre"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    artists: Mapped[list["Artist"]] = db.relationship(
        "Artist",
        secondary=artist_genre,
        lazy="subquery",
        backref=db.backref("Genre", lazy=True),
        viewonly=True,
    )

    venues: Mapped[list["Venue"]] = db.relationship(
        "Venue",
        secondary=venue_genre,
        lazy="subquery",
        backref=db.backref("Genre", lazy=True),
        viewonly=True,
    )
