from enum import Enum
from typing import Self

from pydantic import field_serializer

from fyyur.models.genre import Genre
from fyyur.schema.base import BaseSchema


class GenreEnum(Enum):
    Alternative = "Alternative"
    Blues = "Blues"
    Classical = "Classical"
    Country = "Country"
    Electronic = "Electronic"
    Folk = "Folk"
    Funk = "Funk"
    HipHop = "Hip-Hop"
    HeavyMetal = "Heavy Metal"
    Instrumental = "Instrumental"
    Jazz = "Jazz"
    MusicalTheatre = "Musical Theatre"
    Pop = "Pop"
    Punk = "Punk"
    RAndB = "R&B"
    Reggae = "Reggae"
    RockNRoll = "Rock n Roll"
    Soul = "Soul"
    Other = "Other"


class GenreInDb(BaseSchema):
    id: int | None = None
    name: GenreEnum

    def to_orm(self) -> Genre:
        return self.to_orm_base(Genre)

    @field_serializer("name", return_type=str)
    def serialize_name(self, name: GenreEnum) -> str:
        return name.value

    @classmethod
    def from_enum(cls, genre_enum: GenreEnum) -> Self:
        return Self(name=genre_enum)

    @classmethod
    def from_str(cls, name: str) -> Self:
        return Self(name=name)
