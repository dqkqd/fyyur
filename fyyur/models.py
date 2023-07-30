import sqlalchemy as sa
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped

from fyyur.schema.show import ShowBase, ShowInArtistInfo, ShowInDb, ShowResponse

db = SQLAlchemy()
migrate = Migrate()


venue_genre = db.Table(
    "venue_genres",
    sa.Column("venue_id", sa.Integer, sa.ForeignKey("Venue.id"), primary_key=True),
    sa.Column("genre_id", sa.Integer, sa.ForeignKey("Genre.id"), primary_key=True),
)


artist_genre = db.Table(
    "artist_genres",
    sa.Column("artist_id", sa.Integer, sa.ForeignKey("Artist.id"), primary_key=True),
    sa.Column("genre_id", sa.Integer, sa.ForeignKey("Genre.id"), primary_key=True),
)


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


class Artist(db.Model):
    __tablename__ = "Artist"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    city = sa.Column(sa.String(120))
    state = sa.Column(sa.String(120))
    phone = sa.Column(sa.String(120))

    image_link = sa.Column(sa.String(500), nullable=True)
    facebook_link = sa.Column(sa.String(120), nullable=True)
    website_link = sa.Column(sa.String(120), nullable=True)

    seeking_venue = sa.Column(sa.Boolean, default=False)
    seeking_description = sa.Column(sa.String)

    shows: Mapped[list["Show"]] = db.relationship("Show", backref="Artist", lazy=True)

    genres: Mapped[list["Genre"]] = db.relationship(
        "Genre",
        secondary=artist_genre,
        lazy="subquery",
        backref=db.backref("Artist", lazy=True),
    )


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


class Show(db.Model):
    __tablename__ = "Show"

    id = sa.Column(sa.Integer, primary_key=True)
    artist_id = sa.Column(sa.Integer, sa.ForeignKey("Artist.id"))
    venue_id = sa.Column(sa.Integer, sa.ForeignKey("Venue.id"))
    start_time = sa.Column(sa.DateTime)

    artist: Mapped["Artist"] = db.relationship(
        "Artist", back_populates="shows", viewonly=True
    )
    venue: Mapped["Venue"] = db.relationship(
        "Venue", back_populates="shows", viewonly=True
    )

    def to_show_base(self) -> ShowBase:
        return ShowBase.model_validate(self)

    def to_show_in_db(self) -> ShowInDb:
        return ShowInDb.model_validate(self)

    def to_show_response(self) -> ShowResponse:
        return ShowResponse(
            venue_id=self.venue.id,
            artist_id=self.artist.id,
            start_time=self.start_time,
            venue_name=self.venue.name,
            artist_name=self.artist.name,
            artist_image_link=self.artist.image_link,
        )

    def to_show_in_artist_info(self) -> ShowInArtistInfo:
        return ShowInArtistInfo(
            venue_id=self.venue_id,
            venue_name=self.venue.name,
            venue_image_link=self.venue.image_link,
            start_time=self.start_time,
        )
