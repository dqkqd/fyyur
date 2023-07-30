from fyyur.models.venue import Venue
from fyyur.schema.base import BaseSchema
from fyyur.schema.show import ShowInDb


class VenueBase(BaseSchema):
    id: int

    def to_orm(self) -> Venue:
        return self.to_orm_base(Venue)


class VenueInDb(VenueBase):
    name: str | None = None
    city: str | None = None
    state: str | None = None
    address: str | None = None
    phone: str | None = None
    image_link: str | None = None
    facebook_link: str | None = None

    shows: list[ShowInDb] = []
