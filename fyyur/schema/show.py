from datetime import datetime

from pydantic import HttpUrl, field_serializer

from fyyur.model import Show
from fyyur.schema.base import BaseSchema


class ShowBase(BaseSchema):
    venue_id: int
    artist_id: int
    start_time: datetime

    def to_orm(self) -> Show:
        return self.to_orm_base(Show)


class ShowInDb(ShowBase):
    id: int | None = None


class ShowResponse(ShowBase):
    venue_name: str
    artist_name: str
    artist_image_link: HttpUrl

    @field_serializer("artist_image_link")
    def serialize_url(self, url: HttpUrl) -> str:
        return str(url)
