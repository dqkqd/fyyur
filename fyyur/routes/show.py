from flask import Blueprint, current_app, flash, render_template

from fyyur.forms import ShowForm
from fyyur.model import Artist, Show, Venue
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
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash("Show was successfully listed!")
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
                    artist_image_link=artist.image_link
                ).model_dump(mode="json")
            )
    return shows_response
