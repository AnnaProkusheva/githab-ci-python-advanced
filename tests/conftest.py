import pytest
from app import create_app, db
from app.models import Client, Parking, ClientParking
from datetime import datetime


@pytest.fixture(scope="session")
def app():
    app = create_app('test')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db


@pytest.fixture
def sample_data(db_session):
    client = Client(name="Иван", surname="Иванов", credit_card="1234-5678")
    parking = Parking(address="ул. Ленина 1", opened=True, count_places=10, count_available_places=5)

    db.session.add(client)
    db.session.add(parking)
    db.session.commit()

    session = ClientParking(client_id=client.id, parking_id=parking.id)
    db.session.add(session)
    db.session.commit()

    return client.id, parking.id