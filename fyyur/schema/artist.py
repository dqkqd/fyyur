from pydantic import HttpUrl, field_serializer

from fyyur.schema.base import BaseSchema, State
from fyyur.schema.genre import GenreEnum, GenreInDb
from fyyur.schema.show import ShowInArtistInfo, ShowInDb


class ArtistBase(BaseSchema):
    name: str | None = None


class ArtistSearchResponse(ArtistBase):
    num_upcoming_shows: int = 0


class ArtistBasicInfoBase(ArtistBase):
    city: str | None = None
    state: State | None = None
    phone: str | None = None

    image_link: HttpUrl | None = None
    facebook_link: HttpUrl | None = None
    website_link: HttpUrl | None = None

    seeking_venue: bool = False
    seeking_description: str | None = None

    @field_serializer("image_link", "facebook_link", "website_link", return_type=str)
    def serialize_url(self, url: HttpUrl) -> str:
        return str(url)

    @field_serializer("state")
    def serialize_state(self, state: State | None) -> str | None:
        if state is None:
            return None
        return state.value


class ArtistBasicInfo(ArtistBasicInfoBase):
    genres: list[GenreEnum] = []


class ArtistInDb(ArtistBasicInfoBase):
    id: int
    shows: list[ShowInDb] = []
    genres: list[GenreInDb] = []

    def to_artist_basic_info(self) -> ArtistBasicInfo:
        return ArtistBasicInfo(
            **self.model_dump(exclude={"id", "shows", "genres"}),
            genres=[GenreEnum(genre.name) for genre in self.genres]
        )


class ArtistInfoResponse(ArtistBasicInfoBase):
    past_shows: list[ShowInArtistInfo]
    upcoming_shows: list[ShowInArtistInfo]
    past_shows_count: int
    upcoming_shows_count: int
