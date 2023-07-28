from datetime import datetime

from fyyur.schema.base import BaseSchema


class ShowSchema(BaseSchema):
    venue_id: int
    artist_id: int
    start_time: datetime
