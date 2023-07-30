from datetime import datetime
from typing import Self

from pydantic import HttpUrl, field_serializer

from fyyur.model import Artist, Show
from fyyur.schema.base import BaseSchema, State
from fyyur.schema.genre import GenreInDb
from fyyur.schema.show import ShowInArtistInfo, ShowInDb


class ArtistBase(BaseSchema):
    id: int

    def to_orm(self) -> Artist:
        return self.to_orm_base(Artist)


class ArtistWithName(ArtistBase):
    name: str | None = None


class ArtistInDbBase(ArtistWithName):
    city: str | None = None
    state: State | None = None
    phone: str | None = None

    image_link: HttpUrl | None = None
    facebook_link: HttpUrl | None = None
    website_link: HttpUrl | None = None

    seeking_venue: bool = False
    seeking_description: str | None = None

    genres: list[GenreInDb] = []

    @field_serializer("image_link", "facebook_link", "website_link", return_type=str)
    def serialize_url(self, url: HttpUrl) -> str:
        return str(url)

    @field_serializer("state")
    def serialize_state(self, state: State | None) -> str | None:
        if state is None:
            return None
        return state.value


class ArtistInDb(ArtistInDbBase):
    shows: list[ShowInDb] = []


class ArtistSearchResponse(ArtistWithName):
    num_upcoming_shows: int = 0

    @classmethod
    def from_artist(cls, artist: Artist) -> Self:
        artist_search_response = cls.model_validate(artist)
        artist_search_response.num_upcoming_shows = len(
            [show for show in artist.shows if show.start_time >= datetime.now()]
        )
        return artist_search_response


class ArtistInfoResponse(ArtistInDbBase):
    past_shows: list[ShowInArtistInfo]
    upcoming_shows: list[ShowInArtistInfo]
    past_shows_count: int
    upcoming_shows_count: int

    @classmethod
    def from_artist(cls, artist: Artist) -> Self:
        artist_in_db_base = ArtistInDbBase.model_validate(artist)

        def is_past(show: Show) -> bool:
            return show.start_time < datetime.now()

        def is_future(show: Show) -> bool:
            return not is_past(show)

        past_shows = list(map(ShowInArtistInfo.from_show, filter(is_past, artist.shows)))
        upcoming_shows = list(
            map(ShowInArtistInfo.from_show, filter(is_future, artist.shows))
        )

        return cls(
            **artist_in_db_base.model_dump(),
            past_shows=past_shows,
            upcoming_shows=upcoming_shows,
            past_shows_count=len(past_shows),
            upcoming_shows_count=len(upcoming_shows)
        )
