import pytest

from app.models import Client, Parking, ClientParking


@pytest.mark.parametrize("endpoint", [
    "/clients",
    "/parkings"
])
def test_get_methods_return_200(client, endpoint):
    response = client.get(endpoint)
    assert response.status_code == 200

def test_create_client(client):
    response = client.post('/clients', json={
        'name': 'Петр', 'surname': 'Петров', 'credit_card': '1111-2222'
    })
    assert response.status_code == 201
    data = response.json
    assert 'id' in data
    client_obj = Client.query.get(data['id'])
    assert client_obj.name == 'Петр'

def test_create_parking(client):
    response = client.post('/parkings', json={
        'address': 'ул. Мира 10', 'opened': True,
        'count_places': 20, 'count_available_places': 15
    })
    assert response.status_code == 201
    data = response.json
    assert 'id' in data
    parking = Parking.query.get(data['id'])
    assert parking.address == 'ул. Мира 10'

@pytest.mark.parking
def test_client_enter_parking(client, sample_data):
    client_id, parking_id = sample_data
    response = client.post('/client_parkings', json={'client_id': client_id, 'parking_id': parking_id})
    assert response.status_code == 400  # Уже заехал

@pytest.mark.parking
def test_client_leave_parking(client, sample_data):
    client_id, parking_id = sample_data
    response = client.delete('/client_parkings', json={'client_id': client_id, 'parking_id': parking_id})
    assert response.status_code == 200
    session = ClientParking.query.filter_by(client_id=client_id, parking_id=parking_id).first()
    assert session.time_out is not None