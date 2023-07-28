from datetime import datetime

from pydantic import HttpUrl

from fyyur.schema.base import BaseSchema


class ShowSchema(BaseSchema):
    venue_id: int
    artist_id: int
    start_time: datetime


class ShowResponse(ShowSchema):
    venue_name: str
    artist_name: str
    artist_image_link: HttpUrl
