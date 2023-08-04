from pydantic import HttpUrl, field_serializer
from pydantic.dataclasses import dataclass

from fyyur.schema.base import BaseSchema, State
from fyyur.schema.genre import GenreEnum, GenreInDb
from fyyur.schema.show import ShowInDb, ShowInVenueInfo


class VenueBase(BaseSchema):
    name: str


class VenueResponse(VenueBase):
    id: int
    num_upcoming_shows: int | None = None


class VenueEditReponse(VenueBase):
    id: int


@dataclass(frozen=True)
class VenueLocation:
    city: str
    state: str


class VenueResponseList(BaseSchema):
    city: str
    state: str
    venues: list[VenueResponse]


class VenueInfo(VenueBase):
    address: str
    city: str
    state: State
    phone: str | None = None

    image_link: HttpUrl | None
    facebook_link: HttpUrl | None = None
    website_link: HttpUrl | None = None

    seeking_talent: bool = False
    seeking_description: str | None = None

    @field_serializer("image_link", "facebook_link", "website_link", return_type=str)
    def serialize_url(self, url: HttpUrl) -> str:
        return str(url)

    @field_serializer("state")
    def serialize_state(self, state: State | None) -> str | None:
        if state is None:
            return None
        return state.value


class VenueInForm(VenueInfo):
    genres: list[GenreEnum]

    @field_serializer("genres")
    def serialize_genres(self, genres: list[GenreEnum]) -> list[str] | None:
        return [genre.value for genre in genres]


class VenueInDb(VenueInfo):
    id: int
    shows: list[ShowInDb] = []
    genres: list[GenreInDb] = []


class VenueInfoResponse(VenueInForm):
    id: int
    past_shows: list[ShowInVenueInfo] = []
    upcoming_shows: list[ShowInVenueInfo] = []
    past_shows_count: int = 0
    upcoming_shows_count: int = 0
