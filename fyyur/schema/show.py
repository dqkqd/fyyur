from datetime import datetime
from typing import Optional

from pydantic import HttpUrl, field_serializer

from fyyur.schema.base import BaseSchema


class ShowBase(BaseSchema):
    venue_id: int
    artist_id: int
    start_time: datetime


class ShowInDb(ShowBase):
    id: Optional[int] = None


class ShowInForm(ShowBase):
    pass


class ShowResponse(ShowBase):
    venue_name: str
    artist_name: str
    artist_image_link: HttpUrl

    @field_serializer("artist_image_link")
    def serialize_url(self, url: HttpUrl) -> str:
        return str(url)


class ShowInArtistInfo(BaseSchema):
    venue_id: int
    venue_name: str
    venue_image_link: HttpUrl
    start_time: datetime

    @field_serializer("venue_image_link")
    def serialize_url(self, url: HttpUrl) -> str:
        return str(url)


class ShowInVenueInfo(BaseSchema):
    artist_id: int
    artist_name: str
    artist_image_link: HttpUrl
    start_time: datetime

    @field_serializer("artist_image_link")
    def serialize_url(self, url: HttpUrl) -> str:
        return str(url)
