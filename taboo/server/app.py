# -*- coding: utf-8 -*-
import logging

from flask import Flask
from flask_bootstrap import Bootstrap

from .ext import db
from .genotype import genotype_bp


def create_app(app_name, config_obj):
    """Flask app factory."""
    app = Flask(app_name)

    # configure app
    app.config['SECRET_KEY'] = 'testing'
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    app.config.update(config_obj)

    # configure extensions
    Bootstrap(app)
    db.init_app(app)

    # register blueprints
    app.register_blueprint(genotype_bp)

    # configure logging
    configure_logging(app)

    return app


def configure_logging(app):
    """Configure file logging"""
    if app.debug or app.testing:
        # Skip debug and test mode; just check standard output
        return

    # Set info level on logger which might be overwritten by handlers
    # Suppress DEBUG messages
    app.logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(
      '%(asctime)s - %(name)s - %(levelname)s: %(message)s '
      '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(stream_handler)

    # also write default Weekzeug log (INFO) to the main log-file
    # note: this is only relevant when not running behind gunicorn
    werkzeug_log = logging.getLogger('werkzeug')
    werkzeug_log.setLevel(logging.INFO)
    werkzeug_log.addHandler(stream_handler)
