from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from fyyur.models import db
from fyyur.models.reference import venue_genre

if TYPE_CHECKING:
    from fyyur.models.genre import Genre
    from fyyur.models.show import Show


class Venue(db.Model):
    __tablename__ = "Venue"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    city = sa.Column(sa.String(120))
    state = sa.Column(sa.String(120))
    address = sa.Column(sa.String(120))
    phone = sa.Column(sa.String(120))

    image_link = sa.Column(sa.String(500), nullable=True)
    facebook_link = sa.Column(sa.String(120), nullable=True)
    website_link = sa.Column(sa.String(120), nullable=True)

    seeking_talent = sa.Column(sa.Boolean, default=False)
    seeking_description = sa.Column(sa.String)

    shows: Mapped[list["Show"]] = db.relationship("Show", backref="Venue", lazy=True)

    genres: Mapped[list["Genre"]] = db.relationship(
        "Genre",
        secondary=venue_genre,
        lazy="subquery",
        backref=db.backref("Venue", lazy=True),
    )
