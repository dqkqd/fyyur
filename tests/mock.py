from datetime import datetime, timedelta

from fyyur.constant import DATETIME_FORMAT
from fyyur.model import Artist, Show, Venue
from fyyur.schema.artist import ArtistInDb
from fyyur.schema.show import ShowInDb
from fyyur.schema.venue import VenueInDb


def date_future(days: int = 1) -> datetime:
    return (datetime.now() + timedelta(days=days)).strftime(DATETIME_FORMAT)


def date_past(days: int = 1) -> datetime:
    return (datetime.now() - timedelta(days=days)).strftime(DATETIME_FORMAT)


def mock_venue(id: int, name: str | None = None) -> VenueInDb:
    name = name if name is not None else f"Venue{id}"
    return VenueInDb(id=id, name=name)


def mock_venues_db() -> list[Venue]:
    return [mock_venue(id).to_orm() for id in range(1, 4)]


def mock_artist(id: int, name: str = None) -> ArtistInDb:
    name = name if name is not None else f"Artist{id}"
    return ArtistInDb(id=id, name=name, image_link=f"https://example{id}.com")


def mock_artists_db() -> list[Artist]:
    return [mock_artist(id).to_orm() for id in range(1, 5)]


def mock_show(
    venue_id: int, artist_id: int, day_offset: int, id: int | None = None
) -> ShowInDb:
    start_time = date_future(day_offset) if day_offset > 0 else date_past(-day_offset)
    return ShowInDb(id=id, venue_id=venue_id, artist_id=artist_id, start_time=start_time)


def mock_shows_db() -> list[Show]:
    return [
        mock_show(id=1, venue_id=1, artist_id=1, day_offset=1).to_orm(),
        mock_show(id=2, venue_id=1, artist_id=1, day_offset=2).to_orm(),
        mock_show(id=3, venue_id=2, artist_id=2, day_offset=3).to_orm(),
        mock_show(id=4, venue_id=1, artist_id=3, day_offset=4).to_orm(),
        mock_show(id=5, venue_id=2, artist_id=4, day_offset=-4).to_orm(),
    ]
