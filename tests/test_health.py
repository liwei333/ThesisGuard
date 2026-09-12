"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test GET /api/v1/health."""

    def test_health_returns_200(self, client: TestClient):
        """Health endpoint should return 200."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_returns_status_ok(self, client: TestClient):
        """Health endpoint should return status ok."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
        assert "version" in data

    def test_health_service_name(self, client: TestClient):
        """Health endpoint should return correct service name."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert data["service"] == "ThesisGuard"


class TestRootEndpoint:
    """Test GET /."""

    def test_root_returns_info(self, client: TestClient):
        """Root endpoint should return app info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestDocsEndpoints:
    """Test API documentation endpoints."""

    def test_swagger_docs_accessible(self, client: TestClient):
        """Swagger UI should be accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema_accessible(self, client: TestClient):
        """OpenAPI schema should be accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "paths" in data
        assert "/api/v1/health" in data["paths"]
        assert "/api/v1/system/status" in data["paths"]
