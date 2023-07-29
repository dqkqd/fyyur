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

from fyyur.constant import DATETIME_FORMAT
from fyyur.schema.base import State
from fyyur.schema.genre import GenreEnum


class ConverterMixin:
    @staticmethod
    def choices(enum_class: Enum) -> list[str]:
        return [e.value for e in enum_class]

    @staticmethod
    def coerce(enum_class: Enum) -> Callable[[str], Enum]:
        def inner(item: Any) -> Enum:
            return enum_class(item)

        return inner


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
        "start_time",
        validators=[DataRequired()],
        default=datetime.today(),
        format=DATETIME_FORMAT,
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
        choices=ConverterMixin.choices(GenreEnum),
        coerce=ConverterMixin.coerce(GenreEnum),
    )
    facebook_link = StringField("facebook_link", validators=[URL()])

    website_link = StringField("website_link")

    seeking_description = StringField("seeking_description")


class VenueForm(ArtistVenueBaseForm):
    address = StringField("address", validators=[DataRequired()])
    seeking_talent = BooleanField("seeking_talent")


class ArtistForm(ArtistVenueBaseForm):
    seeking_venue = BooleanField("seeking_venue")
