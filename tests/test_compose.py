"""Regression tests for Docker Compose topology."""

from pathlib import Path


def test_compose_does_not_require_external_minio_client_image() -> None:
    """Compose startup should not depend on the separate minio/mc image."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "minio/mc:latest" not in compose
    assert "minio-init:" not in compose
