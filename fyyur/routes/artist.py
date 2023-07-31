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
    artist = get_artist_info(artist_id)
    if artist is None:
        abort(404)
    form = ArtistForm(**artist.model_dump())
    return render_template(
        "forms/edit_artist.html", form=form, artist=ArtistResponse.model_validate(artist)
    )


@bp.route("/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id: int) -> FlaskResponse:
    form = ArtistForm()
    ok = update_artist(form, artist_id)
    if ok:
        return redirect(url_for("artist.show_artist", artist_id=artist_id))
    return redirect(url_for("artist.edit_artist", artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------


@bp.route("/create", methods=["GET"])
def create_artist_form() -> str:
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@bp.route("/create", methods=["POST"])
def create_artist_submission() -> FlaskResponse | str:
    form = ArtistForm()
    ok = insert_artist(form)
    if ok:
        return render_template("pages/home.html")
    return redirect(url_for("artist.create_artist_form"))


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


def form_to_artist(form: ArtistForm) -> ArtistInForm | None:
    if not form.validate_on_submit():
        for error in form.errors.values():
            for e in error:
                flash(e, "error")
        return None

    try:
        artist_in_form = ArtistInForm.model_validate(form.data)
    except ValidationError as e:
        flash(str(e), "error")
        return None

    return artist_in_form


def insert_artist(form: ArtistForm) -> bool:
    artist_in_form = form_to_artist(form)
    if artist_in_form is None:
        return False

    artist = artist_in_form.to_orm(Artist)
    artist.genres = Genre.genres_in_and_out_db(artist_in_form.genres)

    ok: bool = True
    try:
        db.session.add(artist)
        db.session.commit()

        flash(f"Artist: {artist_in_form.name} was successfully listed!")

    except Exception as e:
        db.session.rollback()
        ok = False

        flash(str(e), "error")

    finally:
        db.session.close()

    return ok


def update_artist(form: ArtistForm, artist_id: int) -> bool:
    artist_in_form = form_to_artist(form)
    if artist_in_form is None:
        return False

    artist = Artist.query.filter_by(id=artist_id).first()

    if artist is None:
        flash("Artist doesn't exist")
        return False

    artist.genres = Genre.genres_in_and_out_db(artist_in_form.genres)

    artist_info = ArtistInfo(**artist_in_form.model_dump())
    for key, value in artist_info.model_dump().items():
        setattr(artist, key, value)

    db.session.commit()
    return True
