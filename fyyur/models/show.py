from fyyur.models import db


class Show(db.Model):
    __tablename__ = "Show"
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"))
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"))
    start_time = db.Column(db.DateTime)

    artist = db.relationship("Artist", back_populates="shows", viewonly=True)
    venue = db.relationship("Venue", back_populates="shows", viewonly=True)
