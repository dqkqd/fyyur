from fyyur.models import db
from fyyur.schema.show import ShowBase, ShowInArtistInfo, ShowInDb, ShowResponse


class Show(db.Model):
    __tablename__ = "Show"
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"))
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"))
    start_time = db.Column(db.DateTime)

    artist = db.relationship("Artist", back_populates="shows", viewonly=True)
    venue = db.relationship("Venue", back_populates="shows", viewonly=True)

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
