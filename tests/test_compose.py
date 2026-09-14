"""Regression tests for Docker Compose topology.

验证基础设施配置的正确性，防止构建或部署时出现常见错误：
1. 不依赖已废弃的 minio/mc 镜像
2. Worker Dockerfile 复制了继承的 requirements-api.txt
3. pip 安装配置了重试和超时
4. Makefile 迁移命令使用项目 Alembic 配置和正确的端口
5. Mypy 使用 explicit-package-bases 避免命名空间冲突
"""

from pathlib import Path


def test_compose_does_not_require_external_minio_client_image() -> None:
    """Compose startup should not depend on the separate minio/mc image."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "minio/mc:latest" not in compose
    assert "minio-init:" not in compose


def test_worker_dockerfile_copies_inherited_requirements() -> None:
    """Worker requirements include API requirements, so both files must be copied."""
    dockerfile = Path("infra/docker/Dockerfile.worker").read_text(encoding="utf-8")
    worker_requirements = Path("requirements-worker.txt").read_text(encoding="utf-8")

    assert "-r requirements-api.txt" in worker_requirements
    assert "COPY requirements-api.txt ." in dockerfile


def test_python_dockerfiles_use_resilient_pip_retries() -> None:
    """Docker builds should tolerate transient package index DNS failures."""
    for dockerfile_path in (
        Path("infra/docker/Dockerfile.api"),
        Path("infra/docker/Dockerfile.worker"),
    ):
        dockerfile = dockerfile_path.read_text(encoding="utf-8")
        assert "pip install --retries 10 --timeout 60 --no-cache-dir" in dockerfile


def test_api_requirements_include_task_dispatch_dependencies() -> None:
    """API imports Dramatiq actors to dispatch worker tasks."""
    tasks_router = Path("apps/api/routers/tasks.py").read_text(encoding="utf-8")
    requirements = Path("requirements-api.txt").read_text(encoding="utf-8")

    assert "from apps.worker.main import" in tasks_router
    assert "dramatiq" in requirements


def test_worker_container_uses_dramatiq_cli_as_foreground_process() -> None:
    """Worker container should keep Dramatiq running in the foreground."""
    dockerfile = Path("infra/docker/Dockerfile.worker").read_text(encoding="utf-8")

    assert 'CMD ["dramatiq", "apps.worker.main"]' in dockerfile


def test_makefile_migration_commands_use_project_alembic_config() -> None:
    """Local migration commands should use the repository Alembic config."""
    makefile = Path("Makefile").read_text(encoding="utf-8")

    assert "alembic -c migrations/alembic.ini upgrade head" in makefile
    assert "alembic -c migrations/alembic.ini revision --autogenerate" in makefile
    assert "alembic -c migrations/alembic.ini downgrade" in makefile


def test_makefile_local_migrations_target_exposed_postgres_port() -> None:
    """Host-run migrations should connect through localhost, not Docker DNS."""
    makefile = Path("Makefile").read_text(encoding="utf-8")

    assert "DATABASE_URL=postgresql+asyncpg://" in makefile
    assert "@127.0.0.1:$${POSTGRES_HOST_PORT:-15432}" in makefile


def test_compose_uses_dedicated_postgres_host_port() -> None:
    """Docker Postgres should not collide with a local PostgreSQL on 5432."""
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert '"${POSTGRES_HOST_PORT:-15432}:5432"' in compose


def test_makefile_typecheck_uses_explicit_package_bases() -> None:
    """Mypy should avoid duplicate module discovery from namespace packages."""
    makefile = Path("Makefile").read_text(encoding="utf-8")

    assert "MYPYPATH=. mypy --explicit-package-bases backend apps --ignore-missing-imports" in makefile
