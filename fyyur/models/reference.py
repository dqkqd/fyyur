from fyyur.models import db

venue_genre = db.Table(
    "venue_genres",
    db.Column("venue_id", db.Integer, db.ForeignKey("Venue.id"), primary_key=True),
    db.Column("genre_id", db.Integer, db.ForeignKey("Genre.id"), primary_key=True),
)


artist_genre = db.Table(
    "artist_genres",
    db.Column("artist_id", db.Integer, db.ForeignKey("Artist.id"), primary_key=True),
    db.Column("genre_id", db.Integer, db.ForeignKey("Genre.id"), primary_key=True),
)
