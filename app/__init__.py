import os

from flask import Flask

from .models import db
from .routes import bp


def create_app(config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///tasks.db"
    )
    if config:
        app.config.update(config)

    db.init_app(app)
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    return app
