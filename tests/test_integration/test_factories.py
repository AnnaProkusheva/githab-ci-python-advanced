import factory
import pytest
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from app import db
from app.models import Client, Parking

fake = Faker('ru_RU')


class ClientFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = factory.Faker('first_name_female')
    surname = factory.Faker('last_name_female')
    credit_card = factory.LazyFunction(
        lambda: fake.credit_card_number() if fake.boolean(chance_of_getting_true=70) else None
    )
    car_number = factory.Faker('license_plate')


class ParkingFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    address = factory.Faker('address')
    opened = factory.Faker('boolean', chance_of_getting_true=70)
    count_places = factory.Faker('pyint', min_value=5, max_value=100)
    count_available_places = factory.LazyAttribute(lambda obj: obj.count_places - 2)


@pytest.mark.integration
def test_create_client_factory(db_session, app):
    with app.app_context():
        # Очистка перед тестом
        Client.query.delete()
        db.session.commit()

        client = ClientFactory.create()
        db.session.flush()
        assert client.id is not None
        assert len(Client.query.all()) == 1


@pytest.mark.integration
def test_create_parking_factory(db_session, app):
    with app.app_context():
        # Очистка перед тестом
        Parking.query.delete()
        db.session.commit()

        parking = ParkingFactory.create()
        db.session.flush()
        assert parking.id is not None
        assert parking.count_available_places < parking.count_places
