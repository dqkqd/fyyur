import logging
from logging import FileHandler, Formatter
from typing import Any

import babel
import dateutil.parser
from flask import Flask, render_template
from flask_moment import Moment

from fyyur.config import Config, NormalConfig
from fyyur.models import Artist, Venue
from fyyur.schema.artist import ArtistResponse
from fyyur.schema.venue import VenueResponse

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):  # type: ignore
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")  # type: ignore


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


def create_app(config_object: type[Config] = NormalConfig) -> Flask:
    # ----------------------------------------------------------------------------#
    # App Config.
    # ----------------------------------------------------------------------------#

    app = Flask(__name__)
    Moment(app)
    app.config.from_object(config_object)
    app.jinja_env.filters["datetime"] = format_datetime

    from fyyur.models import db, migrate

    db.init_app(app)
    migrate.init_app(app, db)

    from fyyur.routes import artist, show, venue

    app.register_blueprint(venue.bp)
    app.register_blueprint(artist.bp)
    app.register_blueprint(show.bp)

    @app.route("/")
    def index() -> str:
        recent_venues = [
            VenueResponse.model_validate(venue)
            for venue in Venue.query.order_by(Venue.create_date.desc()).limit(10).all()
        ]
        recent_artists = [
            ArtistResponse.model_validate(artist)
            for artist in Artist.query.order_by(Artist.create_date.desc()).limit(10).all()
        ]
        return render_template(
            "pages/home.html", recent_venues=recent_venues, recent_artists=recent_artists
        )

    @app.errorhandler(404)
    def not_found_error(error: Any) -> tuple[str, int]:
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error: Any) -> tuple[str, int]:
        return render_template("errors/500.html"), 500

    if not app.debug:
        file_handler = FileHandler("error.log")
        file_handler.setFormatter(
            Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info("errors")

    return app
