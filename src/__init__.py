import logging
from logging import FileHandler, Formatter

import babel
import dateutil.parser
from flask import Flask, render_template
from flask_moment import Moment

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


def create_app(config_object):
    # ----------------------------------------------------------------------------#
    # App Config.
    # ----------------------------------------------------------------------------#

    app = Flask(__name__)
    Moment(app)
    app.config.from_object(config_object)
    app.jinja_env.filters["datetime"] = format_datetime

    from src.model import db

    # # TODO: connect to a local postgresql database
    db.init_app(app)

    from src.routes import artist, show, venue

    app.register_blueprint(venue.bp)
    app.register_blueprint(artist.bp)
    app.register_blueprint(show.bp)

    @app.route("/")
    def index():
        return render_template("pages/home.html")

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("errors/500.html"), 500

    if not app.debug:
        file_handler = FileHandler("error.log")
        file_handler.setFormatter(Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"))
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info("errors")

    return app
