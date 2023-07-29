from datetime import datetime
from typing import Self

from pydantic import HttpUrl, field_serializer

from fyyur.model import Artist
from fyyur.schema.base import BaseSchema
from fyyur.schema.show import ShowInDb


class ArtistBase(BaseSchema):
    id: int

    def to_orm(self) -> Artist:
        return self.to_orm_base(Artist)


class ArtistWithName(ArtistBase):
    name: str | None = None


class ArtistInDb(ArtistWithName):
    city: str | None = None
    state: str | None = None
    phone: str | None = None

    image_link: HttpUrl | None = None
    website: HttpUrl | None = None
    facebook_link: HttpUrl | None = None

    seeking_venue: bool = False
    seeking_description: str | None = None

    shows: list[ShowInDb] = []
    genres: list[str] = []

    @field_serializer("image_link")
    @field_serializer("website")
    @field_serializer("facebook_link")
    def serialize_url(self, url: HttpUrl) -> str:
        return str(url)


class ArtistSearchResponse(ArtistWithName):
    num_upcoming_shows: int = 0

    @classmethod
    def from_artist(cls, artist: Artist) -> Self:
        artist_search_response = cls.model_validate(artist)
        artist_search_response.num_upcoming_shows = len(
            [show for show in artist.shows if show.start_time >= datetime.now()]
        )
        return artist_search_response
