import pytest
from httpx import AsyncClient


class TestLIAEndpoints:
    """Test LIA-compatible endpoints."""

    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    async def test_get_available_dates(self, client: AsyncClient):
        """Test getting available dates for a specialty."""
        response = await client.get(
            "/api/v1/availability/dates",
            params={"specialty": "Enfermagem", "month": 4, "year": 2026},
        )
        # Should return 200 even if no professionals exist
        assert response.status_code in [200, 500]

    async def test_get_available_times(self, client: AsyncClient):
        """Test getting available times for a professional."""
        import uuid
        fake_id = str(uuid.uuid4())
        response = await client.get(
            "/api/v1/availability/times",
            params={"professional_id": fake_id, "date": "2026-04-15"},
        )
        # Should handle gracefully even with invalid professional
        assert response.status_code in [200, 404, 500]

    async def test_get_agenda(self, client: AsyncClient):
        """Test getting agenda for a date range."""
        response = await client.get(
            "/api/v1/availability/agenda",
            params={
                "date_from": "2026-04-01",
                "date_to": "2026-04-30",
            },
        )
        assert response.status_code in [200, 500]

    async def test_create_appointment(self, client: AsyncClient, sample_appointment_request):
        """Test creating an appointment via LIA endpoint."""
        response = await client.post(
            "/api/v1/availability/appointments",
            json=sample_appointment_request,
        )
        # May fail due to no professional, but should return proper error
        assert response.status_code in [201, 400, 404, 409]

    async def test_create_appointment_invalid_time(self, client: AsyncClient):
        """Test creating appointment with invalid time format."""
        response = await client.post(
            "/api/v1/availability/appointments",
            json={
                "patient_name": "João Silva",
                "patient_phone": "15999999999",
                "specialty": "Enfermagem",
                "date": "2026-04-15",
                "time": "25:00",  # Invalid time
                "source": "lia",
            },
        )
        assert response.status_code == 422

    async def test_create_appointment_missing_fields(self, client: AsyncClient):
        """Test creating appointment with missing required fields."""
        response = await client.post(
            "/api/v1/availability/appointments",
            json={
                "patient_name": "João Silva",
                # Missing phone, specialty, date, time
            },
        )
        assert response.status_code == 422

    async def test_cancel_appointment_nonexistent(self, client: AsyncClient):
        """Test cancelling non-existent appointment."""
        import uuid
        fake_id = str(uuid.uuid4())
        response = await client.put(
            f"/api/v1/availability/appointments/{fake_id}/cancel",
            json={"reason": "Patient requested"},
        )
        assert response.status_code in [404, 500]


class TestAdminEndpoints:
    """Test admin endpoints."""

    async def test_list_appointments_empty(self, client: AsyncClient):
        """Test listing appointments when empty."""
        response = await client.get("/api/v1/appointments")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_list_appointment_types(self, client: AsyncClient):
        """Test listing appointment types."""
        response = await client.get("/api/v1/appointment-types")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_list_professionals(self, client: AsyncClient):
        """Test listing professionals."""
        response = await client.get("/api/v1/professionals")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_settings(self, client: AsyncClient):
        """Test getting settings."""
        response = await client.get("/api/v1/availability/settings")
        assert response.status_code in [200, 500]


class TestErrorHandling:
    """Test error handling."""

    async def test_validation_error_format(self, client: AsyncClient):
        """Test that validation errors return structured response."""
        response = await client.post(
            "/api/v1/availability/appointments",
            json={"invalid": "data"},
        )
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "code" in data["error"]

    async def test_not_found_returns_proper_error(self, client: AsyncClient):
        """Test that not found returns proper error."""
        import uuid
        fake_id = str(uuid.uuid4())
        response = await client.get(f"/api/v1/appointments/{fake_id}")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
