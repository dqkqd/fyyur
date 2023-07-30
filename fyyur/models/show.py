from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from fyyur.models import db
from fyyur.schema.show import ShowBase, ShowInArtistInfo, ShowInDb, ShowResponse

if TYPE_CHECKING:
    from fyyur.models.artist import Artist
    from fyyur.models.venue import Venue


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
