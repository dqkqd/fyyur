from fyyur import create_app
from fyyur.config import NormalConfig
from fyyur.models import Artist, Genre, Show, Venue, db
from fyyur.schema.artist import ArtistInDb
from fyyur.schema.genre import GenreBase
from fyyur.schema.show import ShowInDb
from fyyur.schema.venue import VenueInDb

artist1 = ArtistInDb(
    id=4,
    name="Guns N Petals",
    city="San Francisco",
    state="CA",
    phone="326-123-5000",
    website_link="https://www.gunsnpetalsband.com",
    facebook_link="https://www.facebook.com/GunsNPetals",
    seeking_venue=True,
    seeking_description="Looking for shows to perform at in the San Francisco Bay Area!",
    image_link="https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
).to_orm(Artist)

artist2 = ArtistInDb(
    id=5,
    name="Matt Quevedo",
    city="New York",
    state="NY",
    phone="300-400-5000",
    facebook_link="https://www.facebook.com/mattquevedo923251523",
    seeking_venue=False,
    image_link="https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
).to_orm(Artist)

artist3 = ArtistInDb(
    id=6,
    name="The Wild Sax Band",
    city="San Francisco",
    state="CA",
    phone="432-325-5432",
    seeking_venue=False,
    image_link="https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
).to_orm(Artist)

venue1 = VenueInDb(
    id=1,
    name="The Musical Hop",
    address="1015 Folsom Street",
    city="San Francisco",
    state="CA",
    phone="123-123-1234",
    website_link="https://www.themusicalhop.com",
    facebook_link="https://www.facebook.com/TheMusicalHop",
    seeking_talent=True,
    seeking_description="We are on the lookout for a local artist to play every two weeks. Please call us.",  # noqa
    image_link="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
).to_orm(Venue)

venue2 = VenueInDb(
    id=2,
    name="The Dueling Pianos Bar",
    address="335 Delancey Street",
    city="New York",
    state="NY",
    phone="914-003-1132",
    website="https://www.theduelingpianos.com",
    facebook_link="https://www.facebook.com/theduelingpianos",
    seeking_talent=False,
    image_link="https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
).to_orm(Venue)

venue3 = VenueInDb(
    id=3,
    name="Park Square Live Music & Coffee",
    address="34 Whiskey Moore Ave",
    city="San Francisco",
    state="CA",
    phone="415-000-1234",
    website="https://www.parksquarelivemusicandcoffee.com",
    facebook_link="https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    seeking_talent=False,
    image_link="https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
).to_orm(Venue)

show1 = ShowInDb(venue_id=1, artist_id=4, start_time="2019-05-21T21:30:00.000Z").to_orm(
    Show
)
show2 = ShowInDb(venue_id=3, artist_id=5, start_time="2019-06-15T23:00:00.000Z").to_orm(
    Show
)
show3 = ShowInDb(venue_id=3, artist_id=6, start_time="2035-04-01T20:00:00.000Z").to_orm(
    Show
)
show4 = ShowInDb(venue_id=3, artist_id=6, start_time="2035-04-08T20:00:00.000Z").to_orm(
    Show
)
show5 = ShowInDb(venue_id=3, artist_id=6, start_time="2035-04-15T20:00:00.000Z").to_orm(
    Show
)

genre1 = GenreBase(name="Rock n Roll").to_orm(Genre)
genre2 = GenreBase(name="Jazz").to_orm(Genre)
genre3 = GenreBase(name="Classical").to_orm(Genre)
genre4 = GenreBase(name="Reggae").to_orm(Genre)
genre5 = GenreBase(name="Alternative").to_orm(Genre)
genre6 = GenreBase(name="Folk").to_orm(Genre)
genre7 = GenreBase(name="R&B").to_orm(Genre)
genre8 = GenreBase(name="Hip-Hop").to_orm(Genre)

artist1.genres.append(genre1)
artist1.shows.append(show1)

artist2.genres.append(genre2)
artist2.shows.append(show2)

artist3.shows = [show3, show4, show5]
artist3.genres = [genre2, genre3]

venue1.genres = [genre2, genre4, genre5, genre3, genre6]
venue2.genres = [genre3, genre7, genre8]
venue3.genres = [genre1, genre2, genre3, genre6]


app = create_app(NormalConfig)
with app.app_context():
    db.session.add_all([artist1, artist2, artist3, venue1, venue2, venue3])
    db.session.commit()
