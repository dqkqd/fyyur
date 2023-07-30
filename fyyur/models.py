from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fyyur.schema.artist import (
    ArtistBasicInfoBase,
    ArtistInfoResponse,
    ArtistSearchResponse,
)
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

    shows: Mapped[list["Show"]] = relationship("Show", backref="Venue", lazy=True)

    genres: Mapped[list["Genre"]] = relationship(
        "Genre",
        secondary=venue_genre,
        lazy="subquery",
        backref=db.backref("Venue", lazy=True),
    )


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

    shows: Mapped[list["Show"]] = relationship("Show", backref="Artist", lazy=True)

    genres: Mapped[list["Genre"]] = relationship(
        "Genre",
        secondary=artist_genre,
        lazy="subquery",
        backref=db.backref("Artist", lazy=True),
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

    def to_search_response(self) -> ArtistSearchResponse:
        return ArtistSearchResponse(
            name=self.name, num_upcoming_shows=self.upcoming_shows_count
        )

    def to_basic_info_base(self) -> ArtistBasicInfoBase:
        return ArtistBasicInfoBase.model_validate(self)

    def to_info_response(self) -> ArtistInfoResponse:
        basic_info_base = self.to_basic_info_base()
        upcomming_shows = [show.to_show_in_artist_info() for show in self.upcoming_shows]
        past_shows = [show.to_show_in_artist_info() for show in self.past_shows]
        print(self.upcoming_shows_count)
        return ArtistInfoResponse(
            **basic_info_base.model_dump(),
            upcoming_shows=upcomming_shows,
            past_shows=past_shows,
            upcoming_shows_count=self.upcoming_shows_count,
            past_shows_count=self.past_shows_count,
        )


class Genre(db.Model):  # type: ignore
    __tablename__ = "Genre"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    artists: Mapped[list["Artist"]] = relationship(
        "Artist",
        secondary=artist_genre,
        lazy="subquery",
        backref=db.backref("Genre", lazy=True),
        viewonly=True,
    )

    venues: Mapped[list["Venue"]] = relationship(
        "Venue",
        secondary=venue_genre,
        lazy="subquery",
        backref=db.backref("Genre", lazy=True),
        viewonly=True,
    )


class Show(db.Model):  # type: ignore
    __tablename__ = "Show"

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_id: Mapped[int] = mapped_column(sa.ForeignKey("Artist.id"))
    venue_id: Mapped[int] = mapped_column(sa.ForeignKey("Venue.id"))
    start_time: Mapped[datetime]

    artist: Mapped["Artist"] = relationship(
        "Artist", back_populates="shows", viewonly=True
    )
    venue: Mapped["Venue"] = relationship("Venue", back_populates="shows", viewonly=True)

    @property
    def is_past(self) -> bool:
        return self.start_time < datetime.now()

    @property
    def is_future(self) -> bool:
        return not self.is_past

    def to_show_base(self) -> ShowBase:
        return ShowBase.model_validate(self)

    def to_show_in_db(self) -> ShowInDb:
        return ShowInDb.model_validate(self)

    def to_show_response(self) -> ShowResponse:
        return ShowResponse(
            venue_id=self.venue.id,
            artist_id=self.artist.id,
            start_time=self.start_time,
            venue_name=self.venue.name,
            artist_name=self.artist.name,
            artist_image_link=self.artist.image_link,
        )

    def to_show_in_artist_info(self) -> ShowInArtistInfo:
        return ShowInArtistInfo(
            venue_id=self.venue_id,
            venue_name=self.venue.name,
            venue_image_link=self.venue.image_link,
            start_time=self.start_time,
        )