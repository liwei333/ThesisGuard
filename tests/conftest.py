"""Shared test fixtures and configuration."""

import asyncio

import pytest
from apps.api.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """Synchronous test client with short timeout."""
    return TestClient(app, raise_server_exceptions=False)
