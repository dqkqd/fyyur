from enum import Enum
from typing import Optional

from pydantic import field_serializer
from typing_extensions import Self

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


class GenreBase(BaseSchema):
    name: GenreEnum

    @field_serializer("name", return_type=str)
    def serialize_name(self, name: GenreEnum) -> str:
        return name.value

    @classmethod
    def from_enum(cls, genre_enum: GenreEnum) -> Self:
        return cls(name=genre_enum)

    @classmethod
    def from_str(cls, name: str) -> Self:
        return cls(name=name)


class GenreInDb(GenreBase):
    id: Optional[int]
