from datetime import datetime
from enum import Enum
from typing import Any, Callable, TypeVar

import phonenumbers
from flask_wtf import FlaskForm, Form
from phonenumbers import PhoneNumber
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

from fyyur.constant import DATETIME_FORMAT
from fyyur.schema.base import State
from fyyur.schema.genre import GenreEnum

T = TypeVar("T", bound=Enum)


class ConverterMixin:
    @staticmethod
    def choices(enum_class: type[T]) -> list[tuple[T, Any]]:
        return [(e, e.value) for e in enum_class]

    @staticmethod
    def coerce(enum_class: type[T]) -> Callable[[Any], T]:
        def inner(item: Any) -> T:
            return enum_class(item)

        return inner


class PhoneValidator:
    def __init__(self) -> None:
        self.field_flags = {"required": True}

    @staticmethod
    def _parse(number: str) -> PhoneNumber | None:
        for region in ["US", None]:
            phone_number = phonenumbers.parse(number, region)
            if phonenumbers.is_possible_number(phone_number):
                return phone_number
        return None

    def __call__(self, form: Form, field: Any) -> None:
        message = "Phone number is invalid."
        phone_number = PhoneValidator._parse(field.data)
        if phone_number is None:
            raise ValidationError(message)


class CustomDataRequiredValidator(DataRequired):  # type:ignore
    def __init__(self, field: str | None = None):
        message = f"{field} is required." if field else None
        super().__init__(message)


class CustomURLValidator(URL):  # type: ignore
    def __init__(self, require_tld: bool = True, field: str | None = None) -> None:
        message = f"{field} : Invalid URL." if field else None
        super().__init__(require_tld, message)


class ShowForm(FlaskForm):  # type: ignore
    artist_id = IntegerField(
        "artist_id", validators=[CustomDataRequiredValidator("Artist ID")]
    )
    venue_id = IntegerField(
        "venue_id", validators=[CustomDataRequiredValidator("Venue ID")]
    )
    start_time = DateTimeField(
        "start_time",
        validators=[CustomDataRequiredValidator("Start Time")],
        default=datetime.today(),
        format=DATETIME_FORMAT,
    )


class ArtistVenueBaseForm(FlaskForm):  # type: ignore
    name = StringField("name", validators=[CustomDataRequiredValidator("Artist Name")])
    city = StringField("city", validators=[CustomDataRequiredValidator("City")])
    state = SelectField(
        "state",
        validators=[CustomDataRequiredValidator("State")],
        choices=ConverterMixin.choices(State),
        coerce=ConverterMixin.coerce(State),
    )
    phone = StringField("phone", validators=[PhoneValidator()])
    image_link = StringField(
        "image_link", validators=[CustomURLValidator(field="Image Link")]
    )
    genres = SelectMultipleField(
        "genres",
        validators=[CustomDataRequiredValidator("Genre")],
        choices=ConverterMixin.choices(GenreEnum),
        coerce=ConverterMixin.coerce(GenreEnum),
    )
    facebook_link = StringField(
        "facebook_link", validators=[CustomURLValidator(field="Facebook Link")]
    )

    website_link = StringField(
        "website_link", validators=[CustomURLValidator(field="Website Link")]
    )

    seeking_description = StringField("seeking_description")


class VenueForm(ArtistVenueBaseForm):
    address = StringField("address", validators=[CustomDataRequiredValidator("Address")])
    seeking_talent = BooleanField("seeking_talent")


class ArtistForm(ArtistVenueBaseForm):
    seeking_venue = BooleanField("seeking_venue")
