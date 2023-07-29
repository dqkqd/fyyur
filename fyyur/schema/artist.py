from fyyur.schema.base import BaseSchema
from fyyur.schema.show import ShowSchema


class ArtistBaseSchema(BaseSchema):
    id: int
    name: str | None = None


class ArtistSchema(ArtistBaseSchema):
    city: str | None = None
    state: str | None = None
    phone: str | None = None
    genres: str | None = None
    image_link: str | None = None
    facebook_link: str | None = None

    shows: list[ShowSchema] = []
