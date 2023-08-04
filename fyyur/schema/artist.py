from typing import Optional

from pydantic import HttpUrl, field_serializer

from fyyur.schema.base import BaseSchema, State
from fyyur.schema.genre import GenreEnum, GenreInDb
from fyyur.schema.show import ShowInArtistInfo, ShowInDb


class ArtistBase(BaseSchema):
    name: str


class ArtistResponse(ArtistBase):
    id: int


class ArtistSearchResponse(ArtistResponse):
    num_upcoming_shows: int = 0


class ArtistInfo(ArtistBase):
    city: str
    state: State
    phone: Optional[str] = None

    image_link: Optional[HttpUrl] = None
    facebook_link: Optional[HttpUrl] = None
    website_link: Optional[HttpUrl] = None

    seeking_venue: bool = False
    seeking_description: Optional[str] = None

    @field_serializer("image_link", "facebook_link", "website_link", return_type=str)
    def serialize_url(self, url: HttpUrl) -> str:
        return str(url)

    @field_serializer("state")
    def serialize_state(self, state: Optional[State]) -> Optional[str]:
        if state is None:
            return None
        return state.value


class ArtistInForm(ArtistInfo):
    genres: list[GenreEnum]

    @field_serializer("genres")
    def serialize_genres(self, genres: list[GenreEnum]) -> list[str]:
        return [genre.value for genre in genres]


class ArtistInDb(ArtistInfo):
    id: int
    shows: list[ShowInDb] = []
    genres: list[GenreInDb] = []


class ArtistInfoResponse(ArtistInForm):
    id: int
    past_shows: list[ShowInArtistInfo] = []
    upcoming_shows: list[ShowInArtistInfo] = []
    past_shows_count: int = 0
    upcoming_shows_count: int = 0
