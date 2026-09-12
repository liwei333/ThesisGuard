"""Tests for system status endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestSystemStatusEndpoint:
    """Test GET /api/v1/system/status."""

    def test_system_status_returns_200(self, client: TestClient):
        """System status should return 200 even if some services are down."""
        response = client.get("/api/v1/system/status")
        assert response.status_code == 200

    def test_system_status_structure(self, client: TestClient):
        """System status should have correct structure."""
        response = client.get("/api/v1/system/status")
        data = response.json()
        assert "status" in data
        assert "api" in data
        assert "services" in data

    def test_system_status_has_required_services(self, client: TestClient):
        """System status should include all required services."""
        response = client.get("/api/v1/system/status")
        data = response.json()
        services = data["services"]
        assert "postgres" in services
        assert "redis" in services
        assert "object_storage" in services
        assert "worker" in services

    def test_system_status_service_format(self, client: TestClient):
        """Each service should have status and message."""
        response = client.get("/api/v1/system/status")
        data = response.json()
        for service_name, service_data in data["services"].items():
            assert "status" in service_data
            assert "message" in service_data
            assert service_data["status"] in ("ok", "error")
