from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    shows = db.relationship("Show", backref="Venue", lazy=True)


artist_genre = db.Table(
    "artist_genres",
    db.Column("artist_id", db.Integer, db.ForeignKey("Artist.id"), primary_key=True),
    db.Column("genre_id", db.Integer, db.ForeignKey("Genre.id"), primary_key=True),
)


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))

    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)

    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)

    shows = db.relationship("Show", backref="Artist", lazy=True)

    genres = db.relationship(
        "Genre",
        secondary=artist_genre,
        lazy="subquery",
        backref=db.backref("Artist", lazy=True),
    )


class Genre(db.Model):
    __tablename__ = "Genre"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class Show(db.Model):
    __tablename__ = "Show"
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"))
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"))
    start_time = db.Column(db.DateTime)
