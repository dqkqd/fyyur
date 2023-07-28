from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from pydantic import ValidationError

from fyyur.forms import ShowForm
from fyyur.model import Artist, Show, Venue, db
from fyyur.schema.show import ShowResponse, ShowSchema

bp = Blueprint("show", __name__, url_prefix="/shows")


@bp.route("/")
def shows():
    data = get_shows()
    return render_template("pages/shows.html", shows=data)


@bp.route("/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@bp.route("/create", methods=["POST"])
def create_show_submission():
    error = False
    error_msg = "An error occurred. Show could not be listed."

    try:
        show_schema = ShowSchema(**request.form)
        artist_id = show_schema.artist_id
        venue_id = show_schema.venue_id
        if not Artist.query.filter_by(id=artist_id).first():
            error = True
            error_msg = f"Artist with id `{artist_id}` doesn't exists"
        elif not Venue.query.filter_by(id=venue_id).first():
            error = True
            error_msg = f"Venue with id `{venue_id}` doesn't exists"

        if not error:
            with current_app.app_context():
                db.session.add(show_schema.to_orm(Show))
                db.session.commit()

    except ValidationError as e:
        error = True
        if current_app.debug:
            current_app.logger.error(e)

    if error:
        flash(error_msg)
        return redirect(url_for("show.create_shows"))

    flash("Show was successfully listed!")
    return render_template("pages/home.html")


def get_shows():
    """Seperate `get_shows` so we can test this behavior"""
    shows_response = []
    with current_app.app_context():
        shows = Show.query.all()
        for show in shows:
            show_schema = ShowSchema.model_validate(show)
            venue = Venue.query.filter_by(id=show_schema.venue_id).first()
            artist = Artist.query.filter_by(id=show_schema.artist_id).first()
            shows_response.append(
                ShowResponse(
                    **show_schema.model_dump(),
                    venue_name=venue.name,
                    artist_name=artist.name,
                    artist_image_link=artist.image_link,
                ).model_dump(mode="json")
            )
    return shows_response
