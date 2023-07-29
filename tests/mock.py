from datetime import datetime, timedelta

from fyyur.constant import DATETIME_FORMAT
from fyyur.model import Artist, Show, Venue
from fyyur.schema.artist import ArtistInDb
from fyyur.schema.show import ShowBase
from fyyur.schema.venue import VenueInDb


def date_future(days: int = 1) -> datetime:
    return (datetime.now() + timedelta(days=days)).strftime(DATETIME_FORMAT)


def date_past(days: int = 1) -> datetime:
    return (datetime.now() - timedelta(days=days)).strftime(DATETIME_FORMAT)


def mock_venues() -> list[Venue]:
    return [VenueInDb(id=id, name=f"Venue{id}").to_orm() for id in range(1, 4)]


def mock_artists() -> list[Artist]:
    return [
        ArtistInDb(
            id=id, name=f"Artist{id}", image_link=f"https://example{id}.com"
        ).to_orm()
        for id in range(1, 5)
    ]


def mock_shows() -> list[Show]:
    return [
        ShowBase(id=1, venue_id=1, artist_id=1, start_time=date_future(days=1)).to_orm(),
        ShowBase(id=2, venue_id=1, artist_id=1, start_time=date_future(days=2)).to_orm(),
        ShowBase(id=3, venue_id=2, artist_id=2, start_time=date_future(days=3)).to_orm(),
        ShowBase(id=4, venue_id=1, artist_id=3, start_time=date_future(days=4)).to_orm(),
        ShowBase(id=5, venue_id=2, artist_id=4, start_time=date_past(days=4)).to_orm(),
    ]
