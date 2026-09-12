"""Tests for task dispatch endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestTaskDispatch:
    """Test task dispatch endpoints."""

    def test_dispatch_health_check_task(self, client: TestClient):
        """Should be able to dispatch health check task when broker is available."""
        with patch("apps.api.routers.tasks.system_health_task") as mock_task:
            mock_msg = MagicMock()
            mock_msg.message_id = "test-task-id-123"
            mock_task.send.return_value = mock_msg

            response = client.post("/api/v1/tasks/health-check")
            assert response.status_code == 200
            data = response.json()
            assert data["task_id"] == "test-task-id-123"
            assert data["actor"] == "system_health_task"
            assert data["status"] == "queued"

    def test_dispatch_echo_task(self, client: TestClient):
        """Should be able to dispatch echo task when broker is available."""
        with patch("apps.api.routers.tasks.echo_task") as mock_task:
            mock_msg = MagicMock()
            mock_msg.message_id = "test-echo-id-456"
            mock_task.send.return_value = mock_msg

            response = client.post("/api/v1/tasks/echo", json={"message": "hello test"})
            assert response.status_code == 200
            data = response.json()
            assert data["task_id"] == "test-echo-id-456"
            assert data["actor"] == "echo_task"
            assert data["status"] == "queued"

    def test_dispatch_echo_default_message(self, client: TestClient):
        """Echo task should work with default message."""
        with patch("apps.api.routers.tasks.echo_task") as mock_task:
            mock_msg = MagicMock()
            mock_msg.message_id = "test-echo-id-789"
            mock_task.send.return_value = mock_msg

            response = client.post("/api/v1/tasks/echo", json={})
            assert response.status_code == 200

    def test_dispatch_health_check_broker_down(self, client: TestClient):
        """Should return 503 when broker is unavailable."""
        with patch("apps.api.routers.tasks.system_health_task") as mock_task:
            mock_task.send.side_effect = Exception("Connection refused")

            response = client.post("/api/v1/tasks/health-check")
            assert response.status_code == 503
            data = response.json()
            assert "detail" in data
