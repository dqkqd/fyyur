from datetime import datetime
from typing import Self

from pydantic import HttpUrl, field_serializer

from fyyur.model import Show
from fyyur.schema.base import BaseSchema


class ShowBaseAbstract(BaseSchema):
    def to_orm(self) -> Show:
        return self.to_orm_base(Show)

    @classmethod
    def from_show(cls, show: Show) -> Self:
        raise NotImplementedError


class ShowBase(ShowBaseAbstract):
    venue_id: int
    artist_id: int
    start_time: datetime


class ShowInDb(ShowBase):
    id: int | None = None


class ShowResponse(ShowBase):
    venue_name: str
    artist_name: str
    artist_image_link: HttpUrl

    @field_serializer("artist_image_link")
    def serialize_url(self, url: HttpUrl) -> str:
        return str(url)

    @classmethod
    def from_show(cls, show: Show) -> Self:
        return cls(
            venue_id=show.venue_id,
            artist_id=show.artist_id,
            start_time=show.start_time,
            venue_name=show.venue.name,
            artist_name=show.artist.name,
            artist_image_link=show.artist.image_link,
        )


class ShowInArtistInfo(ShowBaseAbstract):
    venue_id: int
    venue_name: str
    venue_image_link: HttpUrl
    start_time: datetime

    @classmethod
    def from_show(cls, show: Show) -> Self:
        return cls(
            venue_id=show.venue_id,
            venue_name=show.venue.name,
            venue_image_link=show.venue.image_link,
            start_time=show.start_time,
        )
