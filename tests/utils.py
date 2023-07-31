from datetime import datetime, timedelta

from fyyur.constant import DATETIME_FORMAT


def date_offset(days: int = 1) -> datetime:
    date = datetime.now() + timedelta(days=days)
    date = date.replace(
        minute=0,
        second=0,
        microsecond=0,
    )
    return date


def date_future(days: int = 1) -> datetime:
    return date_offset(days)


def date_past(days: int = 1) -> datetime:
    return date_offset(-days)


def date_future_str(days: int = 1) -> str:
    return date_future(days).strftime(DATETIME_FORMAT)


def date_past_str(days: int = 1) -> str:
    return date_past(days).strftime(DATETIME_FORMAT)
