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
    genres: str | None = None
    image_link: str | None = None
    facebook_link: str | None = None

    shows: list[ShowInDb] = []

    genres: list[str] = []


class ArtistSearchResponse(ArtistWithName):
    num_upcoming_shows: int = 0
