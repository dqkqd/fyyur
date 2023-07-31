from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fyyur.schema.artist import (
    ArtistBase,
    ArtistInDb,
    ArtistInfo,
    ArtistInfoResponse,
    ArtistInForm,
    ArtistResponse,
    ArtistSearchResponse,
)
from fyyur.schema.genre import GenreBase
from fyyur.schema.show import ShowBase, ShowInArtistInfo, ShowInDb, ShowResponse

db = SQLAlchemy()
migrate = Migrate()


venue_genre = db.Table(
    "venue_genres",
    db.Column("venue_id", sa.Integer, sa.ForeignKey("Venue.id"), primary_key=True),
    db.Column("genre_id", sa.Integer, sa.ForeignKey("Genre.id"), primary_key=True),
)


artist_genre = db.Table(
    "artist_genres",
    db.Column("artist_id", sa.Integer, sa.ForeignKey("Artist.id"), primary_key=True),
    db.Column("genre_id", sa.Integer, sa.ForeignKey("Genre.id"), primary_key=True),
)


class Venue(db.Model):  # type: ignore
    __tablename__ = "Venue"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    # TODO: remove nullable if possible
    city: Mapped[str] = mapped_column(sa.String(120), nullable=True)
    state: Mapped[str] = mapped_column(sa.String(120), nullable=True)
    address: Mapped[str] = mapped_column(sa.String(120), nullable=True)
    phone: Mapped[str] = mapped_column(sa.String(120), nullable=True)

    image_link: Mapped[str] = mapped_column(sa.String(500), nullable=True)
    facebook_link: Mapped[str] = mapped_column(sa.String(120), nullable=True)
    website_link: Mapped[str] = mapped_column(sa.String(120), nullable=True)

    seeking_talent: Mapped[bool] = mapped_column(default=False)
    seeking_description: Mapped[str] = mapped_column(nullable=True)

    shows: Mapped[list["Show"]] = relationship(
        back_populates="venue", lazy=True, cascade="all, delete-orphan"
    )

    genres: Mapped[list["Genre"]] = relationship(secondary=venue_genre, lazy="subquery")


class Artist(db.Model):  # type: ignore
    __tablename__ = "Artist"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    # TODO: remove nullable if possible
    city: Mapped[str] = mapped_column(sa.String(120), nullable=True)
    state: Mapped[str] = mapped_column(sa.String(120), nullable=True)
    phone: Mapped[str] = mapped_column(sa.String(120), nullable=True)

    image_link: Mapped[str] = mapped_column(sa.String(500), nullable=True)
    facebook_link: Mapped[str] = mapped_column(sa.String(120), nullable=True)
    website_link: Mapped[str] = mapped_column(sa.String(120), nullable=True)

    seeking_venue: Mapped[bool] = mapped_column(default=False)
    seeking_description: Mapped[str] = mapped_column(sa.String, nullable=True)

    shows: Mapped[list["Show"]] = relationship(
        back_populates="artist", lazy=True, cascade="all, delete-orphan"
    )

    genres: Mapped[list["Genre"]] = relationship(
        secondary=artist_genre, lazy="subquery", cascade="all, delete"
    )

    @hybrid_property
    def upcoming_shows(self) -> list["Show"]:
        return [show for show in self.shows if show.is_future]

    @hybrid_property
    def past_shows(self) -> list["Show"]:
        return [show for show in self.shows if show.is_past]

    @property
    def upcoming_shows_count(self) -> int:
        return len(self.upcoming_shows)

    @property
    def past_shows_count(self) -> int:
        return len(self.past_shows)

    @property
    def artist_base(self) -> ArtistBase:
        return ArtistBase.model_validate(self)

    @property
    def artist_response(self) -> ArtistResponse:
        return ArtistResponse.model_validate(self)

    @property
    def artist_search_response(self) -> ArtistSearchResponse:
        return ArtistSearchResponse(
            **self.artist_response.model_dump(),
            num_upcoming_shows=self.upcoming_shows_count,
        )

    @property
    def artist_info(self) -> ArtistInfo:
        return ArtistInfo.model_validate(self)

    @property
    def artist_in_form(self) -> ArtistInForm:
        genres = [genre.genre_base for genre in self.genres]
        return ArtistInForm(
            **self.artist_info.model_dump(), genres=[genre.name for genre in genres]
        )

    @property
    def artist_info_response(self) -> ArtistInfoResponse:
        return ArtistInfoResponse(
            id=self.id,
            **self.artist_in_form.model_dump(),
            upcoming_shows=[show.show_in_artist_info for show in self.upcoming_shows],
            past_shows=[show.show_in_artist_info for show in self.past_shows],
            upcoming_shows_count=self.upcoming_shows_count,
            past_shows_count=self.past_shows_count,
        )

    @property
    def artist_in_db(self) -> ArtistInDb:
        return ArtistInDb.model_validate(self)


class Genre(db.Model):  # type: ignore
    __tablename__ = "Genre"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    artists: Mapped[list["Artist"]] = relationship(
        secondary=artist_genre, lazy="subquery", viewonly=True
    )

    venues: Mapped[list["Venue"]] = relationship(
        secondary=venue_genre, lazy="subquery", viewonly=True
    )

    @property
    def genre_base(self) -> GenreBase:
        return GenreBase.model_validate(self)


class Show(db.Model):  # type: ignore
    __tablename__ = "Show"

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_id: Mapped[int] = mapped_column(sa.ForeignKey("Artist.id"))
    venue_id: Mapped[int] = mapped_column(sa.ForeignKey("Venue.id"))
    start_time: Mapped[datetime]

    artist: Mapped["Artist"] = relationship(back_populates="shows", viewonly=True)
    venue: Mapped["Venue"] = relationship(back_populates="shows", viewonly=True)

    @property
    def is_past(self) -> bool:
        return self.start_time < datetime.now()

    @property
    def is_future(self) -> bool:
        return not self.is_past

    @property
    def show_base(self) -> ShowBase:
        return ShowBase.model_validate(self)

    @property
    def show_in_db(self) -> ShowInDb:
        return ShowInDb.model_validate(self)

    @property
    def show_response(self) -> ShowResponse:
        return ShowResponse(
            venue_id=self.venue.id,
            artist_id=self.artist.id,
            start_time=self.start_time,
            venue_name=self.venue.name,
            artist_name=self.artist.name,
            artist_image_link=self.artist.image_link,
        )

    @property
    def show_in_artist_info(self) -> ShowInArtistInfo:
        return ShowInArtistInfo(
            venue_id=self.venue_id,
            venue_name=self.venue.name,
            venue_image_link=self.venue.image_link,
            start_time=self.start_time,
        )
