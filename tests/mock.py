from fyyur.models import Artist, Genre, Show, Venue, db
from fyyur.schema.artist import ArtistInDb
from fyyur.schema.base import State
from fyyur.schema.genre import GenreEnum, GenreInDb
from fyyur.schema.show import ShowInDb
from fyyur.schema.venue import VenueInDb
from tests.utils import date_future_str, date_past_str


def mock_venue(
    id: int,
    name: str | None = None,
    city: str = "San Francisco",
    state: State = State.CA,
    address: str = "123",
) -> VenueInDb:
    name = name if name is not None else f"Venue{id}"

    phone = "326-123-5000"
    name_in_link = name.replace(" ", "").lower()
    image_link = f"https://images.{name_in_link}.com/"
    website_link = f"https://{name_in_link}.com/"
    facebook_link = f"https://www.facebook.com/{name_in_link}/"

    seeking_description = f"{name}: looking for artist."

    return VenueInDb(
        id=id,
        name=name,
        city=city,
        state=state,
        phone=phone,
        address=address,
        image_link=image_link,
        website_link=website_link,
        facebook_link=facebook_link,
        seeking_talent=True,  # put true here so we don't need to exclude or include
        seeking_description=seeking_description,
    )


def mock_venues_db() -> list[Venue]:
    return [mock_venue(id).to_orm(Venue) for id in range(1, 4)]


def mock_artist(
    id: int,
    name: str | None = None,
) -> ArtistInDb:
    name = name if name is not None else f"Artist{id}"

    city = "San Francisco"
    state = "CA"
    phone = "326-123-5000"

    name_in_link = name.replace(" ", "").lower()
    image_link = f"https://images.{name_in_link}.com/"
    website_link = f"https://{name_in_link}.com/"
    facebook_link = f"https://www.facebook.com/{name_in_link}/"

    seeking_description = f"{name} Looking for shows"

    return ArtistInDb(
        id=id,
        name=name,
        city=city,
        state=state,
        phone=phone,
        image_link=image_link,
        website_link=website_link,
        facebook_link=facebook_link,
        seeking_venue=True,  # put true here so we don't need to exclude or include
        seeking_description=seeking_description,
    )


def mock_artists_db() -> list[Artist]:
    return [mock_artist(id).to_orm(Artist) for id in range(1, 5)]


def mock_show(
    venue_id: int, artist_id: int, day_offset: int, id: int | None = None
) -> ShowInDb:
    start_time = (
        date_future_str(day_offset) if day_offset > 0 else date_past_str(-day_offset)
    )
    return ShowInDb(id=id, venue_id=venue_id, artist_id=artist_id, start_time=start_time)


def mock_shows_db() -> list[Show]:
    return [
        mock_show(id=1, venue_id=1, artist_id=1, day_offset=1).to_orm(Show),
        mock_show(id=2, venue_id=1, artist_id=1, day_offset=2).to_orm(Show),
        mock_show(id=3, venue_id=2, artist_id=2, day_offset=3).to_orm(Show),
        mock_show(id=4, venue_id=1, artist_id=3, day_offset=4).to_orm(Show),
        mock_show(id=5, venue_id=2, artist_id=4, day_offset=-4).to_orm(Show),
    ]


def mock_genre(id: int | None, genre: GenreEnum) -> GenreInDb:
    return GenreInDb(id=id, name=genre)


def mock_genres_db() -> list[Genre]:
    return [
        mock_genre(1, GenreEnum.Blues).to_orm(Genre),
        mock_genre(2, GenreEnum.HipHop).to_orm(Genre),
        mock_genre(3, GenreEnum.Jazz).to_orm(Genre),
        mock_genre(4, GenreEnum.RockNRoll).to_orm(Genre),
        mock_genre(5, GenreEnum.Pop).to_orm(Genre),
    ]


def insert_mock_data() -> None:
    venues = mock_venues_db()
    artists = mock_artists_db()
    shows = mock_shows_db()
    genres = mock_genres_db()

    # artist1: blues, hiphop, jazz
    artists[0].genres.append(genres[0])
    artists[0].genres.append(genres[1])
    artists[0].genres.append(genres[2])

    # artist2: jazz, rock n roll, pop
    artists[1].genres.append(genres[2])
    artists[1].genres.append(genres[3])
    artists[1].genres.append(genres[4])

    # artist3: pop
    artists[2].genres.append(genres[4])

    # venue1: blues, hiphop, jazz
    venues[0].genres.append(genres[0])
    venues[0].genres.append(genres[1])
    venues[0].genres.append(genres[2])

    # venue2: jazz, rock n roll, pop
    venues[1].genres.append(genres[2])
    venues[1].genres.append(genres[3])
    venues[1].genres.append(genres[4])

    # venue3: pop
    venues[2].genres.append(genres[4])

    for object in [*venues, *artists, *shows, *genres]:
        db.session.add(object)
