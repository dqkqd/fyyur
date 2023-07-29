from enum import Enum

from fyyur.model import Genre
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
    id: int
    name: GenreEnum

    def to_orm(self) -> Genre:
        return self.to_orm_base(Genre)
