from datetime import datetime, timedelta

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,
)
from pydantic import ValidationError
from sqlalchemy import or_
from werkzeug.wrappers.response import Response as FlaskResponse

from fyyur.forms import ShowForm
from fyyur.models import Artist, Show, Venue, db
from fyyur.schema.show import ShowInForm, ShowResponse

bp = Blueprint("show", __name__, url_prefix="/shows")


@bp.route("/")
def shows() -> str:
    data = [show.model_dump(mode="json") for show in get_shows()]
    return render_template("pages/shows.html", shows=data)


@bp.route("/create")
def create_shows() -> str:
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@bp.route("/create", methods=["POST"])
def create_show_submission() -> FlaskResponse | str:
    form = ShowForm()
    ok = insert_show(form)
    if ok:
        return render_template("pages/home.html")
    return redirect(url_for("show.create_shows"))


def get_shows() -> list[ShowResponse]:
    """Seperate `get_shows` so we can test this behavior"""
    with current_app.app_context():
        shows: list[Show] = Show.query.all()
        return [show.show_response for show in shows]


def insert_show(form: ShowForm) -> bool:
    if not form.validate_on_submit():
        for error in form.errors.values():
            for e in error:
                flash(e, "error")
        return False

    try:
        show = ShowInForm(**form.data)
        artist_id = show.artist_id
        venue_id = show.venue_id
        start_time = show.start_time
    except ValidationError as e:
        flash(str(e), "error")
        return False

    if start_time < datetime.now():
        flash("Could not create show in the past", "error")
        return False

    if (
        not Artist.query.filter_by(id=artist_id).first()
        or not Venue.query.filter_by(id=venue_id).first()
    ):
        flash("Artist or Venue doesn't exist", "error")
        return False

    offset = timedelta(minutes=1)
    existed_shows = (
        Show.query.filter(Show.start_time >= start_time - offset)
        .filter(Show.start_time <= start_time + offset)
        .filter(or_(Show.artist_id == artist_id, Show.venue_id == venue_id))
        .first()
    )
    if existed_shows:
        flash("Show existed", "error")
        return False

    ok: bool = True
    try:
        db.session.add(show.to_orm(Show))
        db.session.commit()

        flash("Show was successfully listed!", "info")

    except Exception as e:
        db.session.rollback()
        ok = False

        flash(str(e), "error")

    finally:
        db.session.close()

    return ok
