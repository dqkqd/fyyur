from fyyur.models import db
from fyyur.models.reference import artist_genre


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))

    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website_link = db.Column(db.String(120), nullable=True)

    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)

    shows = db.relationship("Show", backref="Artist", lazy=True)

    genres = db.relationship(
        "Genre",
        secondary=artist_genre,
        lazy="subquery",
        backref=db.backref("Artist", lazy=True),
    )
