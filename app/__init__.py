from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_name="development", Client=None):
    app = Flask(__name__)

    if config_name == "test":
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    else:
        app.config["DEBUG"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        from app.models import Client, ClientParking, Parking

        db.create_all()

    from app.api import parking

    app.register_blueprint(parking.bp)

    return app