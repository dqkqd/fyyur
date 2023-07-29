from datetime import datetime
from enum import Enum
from typing import Any, Callable, Union

import phonenumbers
from flask_wtf import FlaskForm
from phonenumbers import PhoneNumber, geocoder
from wtforms import (
    BooleanField,
    DateTimeField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    ValidationError,
)
from wtforms.validators import URL, DataRequired


class ConverterMixin:
    @staticmethod
    def choices(enum_class: Enum) -> list[str]:
        return [e.value for e in enum_class]

    @staticmethod
    def coerce(enum_class: Enum) -> Callable[[str], Enum]:
        def inner(item: Any) -> Enum:
            return enum_class(item)

        return inner


class Genres(Enum):
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


class PhoneValidator:
    def __init__(self):
        self.field_flags = {"required": True}

    @staticmethod
    def _parse(number: str) -> PhoneNumber | None:
        for region in ["US", None]:
            phone_number = phonenumbers.parse(number, region)
            if phonenumbers.is_valid_number(phone_number):
                return phone_number
        return None

    def __call__(self, form: Union["VenueForm", "ArtistForm"], field):
        message = "Phone number is invalid."
        phone_number = PhoneValidator._parse(field.data)
        if phone_number is None:
            raise ValidationError(message)

        state = form.state.data
        if state:
            description = geocoder.description_for_valid_number(phone_number, "en")
            if not description.endswith(state):
                raise ValidationError(message)


class ShowForm(FlaskForm):
    artist_id = IntegerField("artist_id", validators=[DataRequired()])
    venue_id = IntegerField("venue_id", validators=[DataRequired()])
    start_time = DateTimeField(
        "start_time", validators=[DataRequired()], default=datetime.today()
    )


class ArtistVenueBaseForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    city = StringField("city", validators=[DataRequired()])
    state = SelectField(
        "state",
        validators=[DataRequired()],
        choices=ConverterMixin.choices(State),
        coerce=ConverterMixin.coerce(State),
    )
    phone = StringField("phone", validators=[PhoneValidator()])
    image_link = StringField("image_link")
    genres = SelectMultipleField(
        "genres",
        validators=[DataRequired()],
        choices=ConverterMixin.choices(Genres),
        coerce=ConverterMixin.coerce(Genres),
    )
    facebook_link = StringField("facebook_link", validators=[URL()])

    website_link = StringField("website_link")

    seeking_description = StringField("seeking_description")


class VenueForm(ArtistVenueBaseForm):
    address = StringField("address", validators=[DataRequired()])
    seeking_talent = BooleanField("seeking_talent")


class ArtistForm(ArtistVenueBaseForm):
    seeking_venue = BooleanField("seeking_venue")
