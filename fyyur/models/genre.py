from fyyur.models import db


class Genre(db.Model):
    __tablename__ = "Genre"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
