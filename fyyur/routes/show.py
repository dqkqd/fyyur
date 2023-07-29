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

from fyyur.forms import ShowForm
from fyyur.model import Artist, Show, Venue, db
from fyyur.schema.show import ShowInDb, ShowResponse

bp = Blueprint("show", __name__, url_prefix="/shows")


@bp.route("/")
def shows():
    data = [show.model_dump(mode="json") for show in get_shows()]
    return render_template("pages/shows.html", shows=data)


@bp.route("/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@bp.route("/create", methods=["POST"])
def create_show_submission():
    form = ShowForm()
    if insert_show(form):
        return render_template("pages/home.html")
    return redirect(url_for("show.create_shows"))


def get_shows() -> list[ShowResponse]:
    """Seperate `get_shows` so we can test this behavior"""
    shows_response = []
    with current_app.app_context():
        shows = Show.query.all()
        for show in shows:
            show_schema = ShowInDb.model_validate(show)
            venue = Venue.query.filter_by(id=show_schema.venue_id).first()
            artist = Artist.query.filter_by(id=show_schema.artist_id).first()
            shows_response.append(
                ShowResponse(
                    **show_schema.model_dump(),
                    venue_name=venue.name,
                    artist_name=artist.name,
                    artist_image_link=artist.image_link,
                )
            )
    return shows_response


def insert_show(form: ShowForm) -> bool:
    if not form.validate_on_submit():
        for error in form.errors.values():
            for e in error:
                flash(e, "error")
        return False

    try:
        show_schema = ShowInDb(**form.data)
        artist_id = show_schema.artist_id
        venue_id = show_schema.venue_id
        start_time = show_schema.start_time

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

        db.session.add(show_schema.to_orm())
        db.session.commit()

    except ValidationError as e:
        flash(e, "error")
        return False

    flash("Show was successfully listed!", "info")
    return True
