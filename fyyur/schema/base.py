from enum import Enum
from typing import TYPE_CHECKING, TypeVar, Union

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from fyyur.models import Artist, Genre, Show, Venue

DbModel = TypeVar("DbModel", bound=Union["Venue", "Artist", "Show", "Genre"])


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    def to_orm(self, orm_class: type[DbModel]) -> DbModel:
        return orm_class(**self.model_dump())


class SearchSchema(BaseModel):
    search_term: str = ""


class State(Enum):
    AL = "AL"
    AK = "AK"
    AZ = "AZ"
    AR = "AR"
    CA = "CA"
    CO = "CO"
    CT = "CT"
    DE = "DE"
    DC = "DC"
    FL = "FL"
    GA = "GA"
    HI = "HI"
    ID = "ID"
    IL = "IL"
    IN = "IN"
    IA = "IA"
    KS = "KS"
    KY = "KY"
    LA = "LA"
    ME = "ME"
    MT = "MT"
    NE = "NE"
    NV = "NV"
    NH = "NH"
    NJ = "NJ"
    NM = "NM"
    NY = "NY"
    NC = "NC"
    ND = "ND"
    OH = "OH"
    OK = "OK"
    OR = "OR"
    MD = "MD"
    MA = "MA"
    MI = "MI"
    MN = "MN"
    MS = "MS"
    MO = "MO"
    PA = "PA"
    RI = "RI"
    SC = "SC"
    SD = "SD"
    TN = "TN"
    TX = "TX"
    UT = "UT"
    VT = "VT"
    VA = "VA"
    WA = "WA"
    WV = "WV"
    WI = "WI"
    WY = "WY"

    def __str__(self) -> str:
        return self.name
