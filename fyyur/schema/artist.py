from fyyur.model import Artist
from fyyur.schema.base import BaseSchema
from fyyur.schema.show import ShowInDb


class ArtistBase(BaseSchema):
    id: int
    name: str | None = None

    def to_orm(self) -> Artist:
        return self.to_orm_base(Artist)


class ArtistInDb(ArtistBase):
    city: str | None = None
    state: str | None = None
    phone: str | None = None
    genres: str | None = None
    image_link: str | None = None
    facebook_link: str | None = None

    shows: list[ShowInDb] = []
