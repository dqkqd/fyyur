import sqlalchemy as sa

from fyyur.models import db

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
