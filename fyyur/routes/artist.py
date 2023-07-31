from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from pydantic import ValidationError
from werkzeug.wrappers.response import Response as FlaskResponse

from fyyur.forms import ArtistForm
from fyyur.models import Artist, Genre, db
from fyyur.schema.artist import (
    ArtistInfo,
    ArtistInfoResponse,
    ArtistInForm,
    ArtistResponse,
    ArtistSearchResponse,
)
from fyyur.schema.base import SearchSchema
from fyyur.schema.genre import GenreBase

bp = Blueprint("artist", __name__, url_prefix="/artists")


@bp.route("/")
def artists() -> str:
    data = [artist.model_dump(mode="json") for artist in get_artists()]
    return render_template("pages/artists.html", artists=data)


@bp.route("/search", methods=["POST"])
def search_artists() -> str:
    search_schema = SearchSchema(**request.form)
    data = [artist.model_dump(mode="json") for artist in find_artists(search_schema)]
    response = {
        "count": len(data),
        "data": data,
    }

    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=search_schema.search_term,
    )


@bp.route("/<int:artist_id>")
def show_artist(artist_id: int) -> str:
    artist = get_artist_info(artist_id)
    if artist is None:
        abort(404)
    return render_template(
        "pages/show_artist.html", artist=artist.model_dump(mode="json")
    )


#  Update
#  ----------------------------------------------------------------
@bp.route("/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id: int) -> str:
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website_link": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@bp.route("/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id: int) -> FlaskResponse:
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for("show_artist", artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------


@bp.route("/create", methods=["GET"])
def create_artist_form() -> str:
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@bp.route("/create", methods=["POST"])
def create_artist_submission() -> FlaskResponse | str:
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = ArtistForm()
    ok = insert_artist(form)
    if ok:
        return render_template("pages/home.html")
    return redirect(url_for("artist.create_artist_form"))

    # on successful db insert, flash success
    flash("Artist " + request.form["name"] + " was successfully listed!")
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template("pages/home.html")


def get_artists() -> list[ArtistResponse]:
    artists: list[Artist] = Artist.query.order_by("id").all()
    return [artist.artist_response for artist in artists]


def find_artists(search: SearchSchema) -> list[ArtistSearchResponse]:
    artists: list[Artist] = Artist.query.filter(
        Artist.name.ilike(f"%{search.search_term}%")
    ).all()
    return [artist.artist_search_response for artist in artists]


def get_artist_info(artist_id: int) -> ArtistInfoResponse | None:
    artist: Artist = Artist.query.filter_by(id=artist_id).first()
    if artist is None:
        return None
    return artist.artist_info_response


def insert_artist(form: ArtistForm) -> bool:
    if not form.validate_on_submit():
        for error in form.errors.values():
            for e in error:
                flash(e, "error")
        return False

    try:
        artist_in_form = ArtistInForm(**form.data)
    except ValidationError as e:
        flash(str(e), "error")
        return False

    artist = ArtistInfo(**form.data).to_orm(Artist)
    artist.genres = [
        GenreBase(name=genre).to_orm(Genre) for genre in artist_in_form.genres
    ]

    ok: bool = True
    try:
        db.session.add(artist)
        db.session.commit()
        flash(f"Artist: {artist_in_form.name} was successfully listed!")
    except Exception as e:
        flash(str(e), "error")
        db.session.rollback()
        ok = False
    finally:
        db.session.close()

    return ok
