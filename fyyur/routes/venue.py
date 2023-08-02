from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from pydantic import ValidationError
from werkzeug.wrappers.response import Response as FlaskResponse

from fyyur.forms import VenueForm
from fyyur.models import Genre, Venue, db
from fyyur.schema.base import SearchSchema
from fyyur.schema.venue import (
    VenueInfoResponse,
    VenueInForm,
    VenueLocation,
    VenueResponse,
    VenueResponseList,
)

bp = Blueprint("venue", __name__, url_prefix="/venues")


@bp.route("/")
def venues() -> str:
    data = [venue.model_dump(mode="json") for venue in get_venues()]
    return render_template("pages/venues.html", areas=data)


@bp.route("/search", methods=["POST"])
def search_venues() -> str:
    search_schema = SearchSchema(**request.form)
    data = [venue.model_dump(mode="json") for venue in find_venues(search_schema)]
    response = {
        "count": len(data),
        "data": data,
    }

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=search_schema.search_term,
    )


@bp.route("/<int:venue_id>")
def show_venue(venue_id: int) -> str:
    venue = get_venue_info(venue_id)
    if venue is None:
        abort(404)
    return render_template("pages/show_venue.html", venue=venue.model_dump(mode="json"))


#  Create Venue
#  ----------------------------------------------------------------


@bp.route("/create", methods=["GET"])
def create_venue_form() -> str:
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@bp.route("/create", methods=["POST"])
def create_venue_submission() -> FlaskResponse | str:
    form = VenueForm()
    ok = insert_venue(form)
    if ok:
        return render_template("pages/home.html")
    return redirect(url_for("venue.create_venue_form"))


@bp.route("/<int:venue_id>", methods=["DELETE"])
def delete_venue(venue_id: int) -> FlaskResponse | str:
    venue: Venue | None = Venue.query.filter_by(id=venue_id).first()
    if venue is None:
        abort(404)

    ok: bool = True
    try:
        db.session.delete(venue)
        db.session.commit()

        flash(f"Venue ID: {venue_id} was successfully deleted!")

    except Exception as e:
        db.session.rollback()
        ok = False

        flash(str(e), "error")

    finally:
        db.session.close()

    return jsonify({"success": ok})


@bp.route("/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id: int) -> str:
    venue = get_venue_info(venue_id)
    if venue is None:
        abort(404)
    form = VenueForm(**venue.model_dump())
    return render_template(
        "forms/edit_venue.html",
        form=form,
        venue=VenueResponse.model_validate(venue).model_dump(
            exclude={"num_upcoming_shows"}
        ),
    )


@bp.route("/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id: int) -> FlaskResponse | str:
    form = VenueForm()
    ok = update_venue(form, venue_id)
    if ok:
        return redirect(url_for("venue.show_venue", venue_id=venue_id))
    return redirect(url_for("venue.edit_venue", venue_id=venue_id))


def get_venues() -> list[VenueResponseList]:
    results: dict[VenueLocation, list[VenueResponse]] = {}
    venues: list[Venue] = Venue.query.order_by("id").all()
    for venue in venues:
        location = VenueLocation(city=venue.city, state=venue.state)
        if location not in results:
            results[location] = []
        results[location].append(venue.venue_response)

    data: list[VenueResponseList] = [
        VenueResponseList(
            city=location.city, state=location.state, venues=venues_response
        )
        for location, venues_response in results.items()
    ]

    return data


def find_venues(search: SearchSchema) -> list[VenueResponse]:
    venues: list[Venue] = Venue.query.filter(
        Venue.name.ilike(f"%{search.search_term}%")
    ).all()
    return [venue.venue_response for venue in venues]


def get_venue_info(venue_id: int) -> VenueInfoResponse | None:
    venue: Venue = Venue.query.filter_by(id=venue_id).first()
    if venue is None:
        return None
    return venue.venue_info_response


def form_to_venue(form: VenueForm) -> VenueInForm | None:
    if not form.validate_on_submit():
        for error in form.errors.values():
            for e in error:
                flash(e, "error")
        return None

    try:
        venue_in_form = VenueInForm.model_validate(form.data)
    except ValidationError as e:
        flash(str(e), "error")
        return None

    return venue_in_form


def insert_venue(form: VenueForm) -> bool:
    venue_in_form = form_to_venue(form)
    if venue_in_form is None:
        return False

    venue = venue_in_form.to_orm(Venue)
    venue.genres = Genre.genres_in_and_out_db(venue_in_form.genres)

    ok: bool = True
    try:
        db.session.add(venue)
        db.session.commit()

        flash(f"Venue: {venue_in_form.name} was successfully listed!")

    except Exception as e:
        db.session.rollback()
        ok = False

        flash(str(e), "error")

    finally:
        db.session.close()

    return ok


def update_venue(form: VenueForm, venue_id: int) -> bool:
    venue_in_form = form_to_venue(form)
    if venue_in_form is None:
        return False

    venue = Venue.query.filter_by(id=venue_id).first()

    if venue is None:
        flash("venue doesn't exist")
        return False

    for key, value in venue_in_form.model_dump(exclude={"genres"}).items():
        setattr(venue, key, value)
    venue.genres = Genre.genres_in_and_out_db(venue_in_form.genres)

    ok: bool = True
    try:
        db.session.commit()

        flash(f"Venue ID: {venue_id} was successfully edited!")

    except Exception as e:
        db.session.rollback()
        ok = False

        flash(str(e), "error")

    finally:
        db.session.close()

    return ok
