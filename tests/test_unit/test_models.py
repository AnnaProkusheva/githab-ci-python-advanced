from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from app.models import ClientParking


@pytest.mark.unit
class TestClientParkingModel:
    @patch.object(ClientParking, 'time_in', datetime.utcnow())
    def test_session_time_in_default(self):
        session = ClientParking(client_id=1, parking_id=1)
        assert session.time_in is not None

    def test_session_time_out_after_time_in(self):
        session = ClientParking(client_id=1, parking_id=1)
        now = datetime.utcnow()
        session.time_in = now
        session.time_out = now - timedelta(hours=1)
        assert session.time_out < session.time_in
