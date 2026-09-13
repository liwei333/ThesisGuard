"""WP-03 Research Package HTTP API contract tests."""

from __future__ import annotations

import asyncio
import os
import subprocess
from collections.abc import AsyncIterator
from uuid import uuid4

import asyncpg
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from apps.api.main import create_app
from backend.common.db.session import get_db

QIANGRUI_INSTRUMENT_ID = "11111111-1111-4111-8111-111111111111"
UNKNOWN_INSTRUMENT_ID = "99999999-9999-4999-8999-999999999999"
DEFAULT_ADMIN_DATABASE_URL = (
    "postgresql+asyncpg://thesisguard:thesisguard_dev_password@127.0.0.1:15432/postgres"
)


@pytest_asyncio.fixture
async def api_sessionmaker() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    """Create one disposable PostgreSQL database for a real API integration test."""
    admin_url = make_url(os.getenv("TG_TEST_ADMIN_DATABASE_URL", DEFAULT_ADMIN_DATABASE_URL))
    test_db_name = f"tg_wp03_api_{uuid4().hex}"
    admin_db = admin_url.database or "postgres"

    admin_conn = await asyncpg.connect(
        user=admin_url.username,
        password=admin_url.password,
        host=admin_url.host or "127.0.0.1",
        port=admin_url.port or 5432,
        database=admin_db,
    )
    await admin_conn.execute(f'CREATE DATABASE "{test_db_name}"')
    await admin_conn.close()

    test_url = admin_url.set(database=test_db_name)
    database_url = test_url.render_as_string(hide_password=False)
    subprocess.run(
        ["alembic", "-c", "migrations/alembic.ini", "upgrade", "head"],
        check=True,
        env={**os.environ, "DATABASE_URL": database_url},
        capture_output=True,
        text=True,
    )

    engine = create_async_engine(database_url, pool_pre_ping=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

    try:
        yield sessionmaker
    finally:
        await engine.dispose()
        cleanup_conn = await asyncpg.connect(
            user=admin_url.username,
            password=admin_url.password,
            host=admin_url.host or "127.0.0.1",
            port=admin_url.port or 5432,
            database=admin_db,
        )
        await cleanup_conn.execute(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = $1 AND pid <> pg_backend_pid()
            """,
            test_db_name,
        )
        await cleanup_conn.execute(f'DROP DATABASE IF EXISTS "{test_db_name}"')
        await cleanup_conn.close()


@pytest_asyncio.fixture
async def research_client(
    api_sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    """Provide a real ASGI client whose DB dependency points at PostgreSQL."""
    app = create_app()

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with api_sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client

    app.dependency_overrides.clear()


def research_path(instrument_id: str) -> str:
    return f"/api/v1/research/instruments/{instrument_id}/packages"


def assert_validation_error_detail(payload: dict, expected_loc_prefix: tuple[str, ...]) -> None:
    """Assert a FastAPI/Pydantic validation error includes the expected location."""
    detail = payload["detail"]
    assert isinstance(detail, list)
    assert any(
        tuple(error.get("loc", ())[: len(expected_loc_prefix)]) == expected_loc_prefix
        for error in detail
    )


def assert_research_validation_error_detail(payload: dict) -> None:
    """Assert a Research domain validation error uses the stable envelope."""
    detail = payload["detail"]
    assert isinstance(detail, dict)
    assert detail["code"] == "RESEARCH_VALIDATION_ERROR"
    assert isinstance(detail["message"], str)


async def create_initial(
    client: AsyncClient,
    instrument_id: str = QIANGRUI_INSTRUMENT_ID,
    key: str = "initial-key",
) -> dict:
    response = await client.post(research_path(instrument_id), headers={"Idempotency-Key": key})
    assert response.status_code == 201
    return response.json()


async def test_create_initial_package_and_replay_are_http_idempotent(
    research_client: AsyncClient,
) -> None:
    """HTTP create returns version 1 modules and replay does not create another version."""
    created = await create_initial(research_client)

    assert created["version"] == 1
    assert created["trigger_type"] == "INITIAL_FULL"
    assert created["status"] == "PENDING"
    assert "request_hash" not in created
    assert "idempotency_key" not in created
    assert len(created["modules"]) == 11
    assert {module["freshness"] for module in created["modules"]} == {"UNVERIFIED"}
    assert all(module["status"] == "UNVERIFIED" for module in created["modules"])
    assert all(module["summary"] is None for module in created["modules"])
    assert all(module["source_refs"] == [] for module in created["modules"])
    assert all("request_hash" not in module for module in created["modules"])

    replay = await research_client.post(
        research_path(QIANGRUI_INSTRUMENT_ID),
        headers={"Idempotency-Key": "initial-key"},
    )
    assert replay.status_code == 201
    assert replay.json()["id"] == created["id"]

    history = await research_client.get(research_path(QIANGRUI_INSTRUMENT_ID))
    assert history.status_code == 200
    assert [package["version"] for package in history.json()] == [1]


async def test_initial_conflicts_have_stable_error_codes(research_client: AsyncClient) -> None:
    """Initial create errors are stable and do not expose internal DB details."""
    await create_initial(research_client, key="initial-a")

    duplicate = await research_client.post(
        research_path(QIANGRUI_INSTRUMENT_ID),
        headers={"Idempotency-Key": "initial-b"},
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"]["code"] == "RESEARCH_PACKAGE_ALREADY_EXISTS"

    missing_instrument = await research_client.post(
        research_path(UNKNOWN_INSTRUMENT_ID),
        headers={"Idempotency-Key": "initial-c"},
    )
    assert missing_instrument.status_code == 404
    assert missing_instrument.json()["detail"]["code"] == "INSTRUMENT_NOT_FOUND"


async def test_current_history_and_specific_version_read_from_postgres(
    research_client: AsyncClient,
    api_sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    """Reads survive a new client/session and are not in-memory state."""
    created = await create_initial(research_client, key="read-back")

    app = create_app()

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with api_sessionmaker() as session:
            yield session
            await session.commit()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        current = await client.get(f"{research_path(QIANGRUI_INSTRUMENT_ID)}/current")
        history = await client.get(research_path(QIANGRUI_INSTRUMENT_ID))
        version_one = await client.get(
            f"{research_path(QIANGRUI_INSTRUMENT_ID)}/versions/1"
        )

    app.dependency_overrides.clear()

    assert current.status_code == 200
    assert current.json()["id"] == created["id"]
    assert history.status_code == 200
    assert [package["version"] for package in history.json()] == [1]
    assert version_one.status_code == 200
    assert version_one.json()["version"] == 1


async def test_refresh_creates_version_two_and_preserves_history(
    research_client: AsyncClient,
) -> None:
    """Refresh creates version 2, current moves forward, and history remains readable."""
    initial = await create_initial(research_client, key="refresh-base")

    refreshed = await research_client.post(
        f"{research_path(QIANGRUI_INSTRUMENT_ID)}/refresh",
        headers={"Idempotency-Key": "refresh-key"},
        json={"expected_version": 1, "module_types": ["FINANCIAL", "RISK"]},
    )
    assert refreshed.status_code == 201
    version_two = refreshed.json()
    assert version_two["version"] == 2
    assert version_two["previous_version_id"] == initial["id"]
    assert version_two["expected_version"] == 1
    assert len(version_two["modules"]) == 11
    assert {module["freshness"] for module in version_two["modules"]} == {"UNVERIFIED"}

    current = await research_client.get(f"{research_path(QIANGRUI_INSTRUMENT_ID)}/current")
    history = await research_client.get(research_path(QIANGRUI_INSTRUMENT_ID))
    version_one = await research_client.get(f"{research_path(QIANGRUI_INSTRUMENT_ID)}/versions/1")

    assert current.status_code == 200
    assert current.json()["version"] == 2
    assert history.status_code == 200
    assert [package["version"] for package in history.json()] == [1, 2]
    assert version_one.status_code == 200
    assert version_one.json()["id"] == initial["id"]


async def test_refresh_request_hash_is_canonical_and_conflicts_are_stable(
    research_client: AsyncClient,
) -> None:
    """Module order is canonicalized while semantic request changes conflict."""
    await create_initial(research_client, key="canonical-base")

    cross_operation_conflict = await research_client.post(
        f"{research_path(QIANGRUI_INSTRUMENT_ID)}/refresh",
        headers={"Idempotency-Key": "canonical-base"},
        json={"expected_version": 1, "module_types": ["FINANCIAL"]},
    )
    assert cross_operation_conflict.status_code == 409
    assert cross_operation_conflict.json()["detail"]["code"] == "IDEMPOTENCY_CONFLICT"

    first = await research_client.post(
        f"{research_path(QIANGRUI_INSTRUMENT_ID)}/refresh",
        headers={"Idempotency-Key": "canonical-refresh"},
        json={"expected_version": 1, "module_types": ["FINANCIAL", "RISK"]},
    )
    assert first.status_code == 201

    replay = await research_client.post(
        f"{research_path(QIANGRUI_INSTRUMENT_ID)}/refresh",
        headers={"Idempotency-Key": "canonical-refresh"},
        json={"expected_version": 1, "module_types": ["RISK", "FINANCIAL"]},
    )
    assert replay.status_code == 201
    assert replay.json()["id"] == first.json()["id"]

    conflict = await research_client.post(
        f"{research_path(QIANGRUI_INSTRUMENT_ID)}/refresh",
        headers={"Idempotency-Key": "canonical-refresh"},
        json={"expected_version": 1, "module_types": ["FINANCIAL"]},
    )
    assert conflict.status_code == 409
    assert conflict.json()["detail"]["code"] == "IDEMPOTENCY_CONFLICT"

    stale = await research_client.post(
        f"{research_path(QIANGRUI_INSTRUMENT_ID)}/refresh",
        headers={"Idempotency-Key": "stale-refresh"},
        json={"expected_version": 1, "module_types": ["COMPANY"]},
    )
    assert stale.status_code == 409
    assert stale.json()["detail"]["code"] == "RESEARCH_VERSION_CONFLICT"
    assert stale.json()["detail"]["expected_version"] == 1
    assert stale.json()["detail"]["current_version"] == 2


async def test_concurrent_http_refresh_allows_only_one_version_two(
    research_client: AsyncClient,
) -> None:
    """Two HTTP refreshes racing on the same expected version cannot both commit."""
    await create_initial(research_client, key="concurrent-http-base")

    async def refresh(key: str) -> tuple[int, str]:
        response = await research_client.post(
            f"{research_path(QIANGRUI_INSTRUMENT_ID)}/refresh",
            headers={"Idempotency-Key": key},
            json={"expected_version": 1, "module_types": ["FINANCIAL"]},
        )
        payload = response.json()
        code = payload.get("detail", {}).get("code", "CREATED")
        return response.status_code, code

    results = await asyncio.gather(refresh("http-race-a"), refresh("http-race-b"))

    assert sorted(results) == [(201, "CREATED"), (409, "RESEARCH_VERSION_CONFLICT")]

    history = await research_client.get(research_path(QIANGRUI_INSTRUMENT_ID))
    assert [package["version"] for package in history.json()] == [1, 2]


async def test_read_and_request_validation_errors(research_client: AsyncClient) -> None:
    """Read misses and request validation errors follow the public contract."""
    empty_history = await research_client.get(research_path(QIANGRUI_INSTRUMENT_ID))
    assert empty_history.status_code == 200
    assert empty_history.json() == []

    current_missing = await research_client.get(f"{research_path(QIANGRUI_INSTRUMENT_ID)}/current")
    assert current_missing.status_code == 404
    assert current_missing.json()["detail"]["code"] == "RESEARCH_PACKAGE_NOT_FOUND"

    missing_version = await research_client.get(
        f"{research_path(QIANGRUI_INSTRUMENT_ID)}/versions/1"
    )
    assert missing_version.status_code == 404
    assert missing_version.json()["detail"]["code"] == "RESEARCH_PACKAGE_NOT_FOUND"

    illegal_version = await research_client.get(
        f"{research_path(QIANGRUI_INSTRUMENT_ID)}/versions/0"
    )
    assert illegal_version.status_code == 422
    assert_validation_error_detail(illegal_version.json(), ("path", "version"))

    missing_header = await research_client.post(research_path(QIANGRUI_INSTRUMENT_ID))
    assert missing_header.status_code == 422
    assert_validation_error_detail(missing_header.json(), ("header", "Idempotency-Key"))

    blank_header = await research_client.post(
        research_path(QIANGRUI_INSTRUMENT_ID),
        headers={"Idempotency-Key": ""},
    )
    assert blank_header.status_code == 422
    assert_validation_error_detail(blank_header.json(), ("header", "Idempotency-Key"))

    whitespace_header = await research_client.post(
        research_path(QIANGRUI_INSTRUMENT_ID),
        headers={"Idempotency-Key": " "},
    )
    assert whitespace_header.status_code == 422
    assert_research_validation_error_detail(whitespace_header.json())

    long_header = await research_client.post(
        research_path(QIANGRUI_INSTRUMENT_ID),
        headers={"Idempotency-Key": "x" * 129},
    )
    assert long_header.status_code == 422
    assert_validation_error_detail(long_header.json(), ("header", "Idempotency-Key"))

    await create_initial(research_client, key="validation-base")

    empty_modules = await research_client.post(
        f"{research_path(QIANGRUI_INSTRUMENT_ID)}/refresh",
        headers={"Idempotency-Key": "empty-modules"},
        json={"expected_version": 1, "module_types": []},
    )
    assert empty_modules.status_code == 422
    assert_validation_error_detail(empty_modules.json(), ("body", "module_types"))

    duplicate_modules = await research_client.post(
        f"{research_path(QIANGRUI_INSTRUMENT_ID)}/refresh",
        headers={"Idempotency-Key": "duplicate-modules"},
        json={"expected_version": 1, "module_types": ["RISK", "RISK"]},
    )
    assert duplicate_modules.status_code == 422
    assert_validation_error_detail(duplicate_modules.json(), ("body", "module_types"))

    unknown_module = await research_client.post(
        f"{research_path(QIANGRUI_INSTRUMENT_ID)}/refresh",
        headers={"Idempotency-Key": "unknown-module"},
        json={"expected_version": 1, "module_types": ["UNKNOWN"]},
    )
    assert unknown_module.status_code == 422
    assert_validation_error_detail(unknown_module.json(), ("body", "module_types"))

    whitespace_refresh_header = await research_client.post(
        f"{research_path(QIANGRUI_INSTRUMENT_ID)}/refresh",
        headers={"Idempotency-Key": " "},
        json={"expected_version": 1, "module_types": ["FINANCIAL"]},
    )
    assert whitespace_refresh_header.status_code == 422
    assert_research_validation_error_detail(whitespace_refresh_header.json())


async def test_openapi_contains_research_contract(research_client: AsyncClient) -> None:
    """OpenAPI exposes the five Research operations and key contracts."""
    response = await research_client.get("/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    paths = openapi["paths"]
    base = "/api/v1/research/instruments/{instrument_id}/packages"

    assert f"{base}" in paths
    assert f"{base}/current" in paths
    assert f"{base}/versions/{{version}}" in paths
    assert f"{base}/refresh" in paths

    assert "post" in paths[base]
    assert "get" in paths[base]
    assert "get" in paths[f"{base}/current"]
    assert "get" in paths[f"{base}/versions/{{version}}"]
    assert "post" in paths[f"{base}/refresh"]

    create_params = paths[base]["post"]["parameters"]
    idempotency_header = next(
        param for param in create_params if param["name"] == "Idempotency-Key"
    )
    assert idempotency_header["in"] == "header"
    assert idempotency_header["required"] is True

    package_schema = openapi["components"]["schemas"]["ResearchPackageRead"]
    module_schema = openapi["components"]["schemas"]["ResearchModuleRead"]
    refresh_schema = openapi["components"]["schemas"]["ResearchRefreshRequest"]
    error_response_schema = openapi["components"]["schemas"]["ResearchErrorResponse"]
    error_detail_schema = openapi["components"]["schemas"]["ResearchErrorDetail"]
    error_code_schema = openapi["components"]["schemas"]["ResearchErrorCode"]
    freshness_schema = module_schema["properties"]["freshness"]
    if "$ref" in freshness_schema:
        freshness_schema = openapi["components"]["schemas"][
            freshness_schema["$ref"].rsplit("/", maxsplit=1)[-1]
        ]

    assert "request_hash" not in package_schema["properties"]
    assert "idempotency_key" not in package_schema["properties"]
    assert "modules" in package_schema["required"]
    assert "freshness" in module_schema["required"]
    assert freshness_schema["enum"] == ["UNVERIFIED", "FRESH", "STALE", "FAILED"]
    assert refresh_schema["required"] == ["expected_version", "module_types"]
    assert error_response_schema["properties"]["detail"]["$ref"].endswith(
        "/ResearchErrorDetail"
    )
    assert error_detail_schema["properties"]["code"]["$ref"].endswith(
        "/ResearchErrorCode"
    )
    assert error_code_schema["enum"] == [
        "INSTRUMENT_NOT_FOUND",
        "RESEARCH_PACKAGE_NOT_FOUND",
        "RESEARCH_PACKAGE_ALREADY_EXISTS",
        "RESEARCH_VERSION_CONFLICT",
        "IDEMPOTENCY_CONFLICT",
        "RESEARCH_VALIDATION_ERROR",
        "RESEARCH_PERSISTENCE_CONFLICT",
        "RESEARCH_DOMAIN_ERROR",
    ]

    assert "HTTPValidationError" in openapi["components"]["schemas"]
    assert "ValidationError" in openapi["components"]["schemas"]

    def response_schema(path: str, method: str, status_code: str) -> dict:
        return paths[path][method]["responses"][status_code]["content"][
            "application/json"
        ]["schema"]

    def assert_ref_resolves(ref: str) -> None:
        _, _, schema_name = ref.rpartition("/")
        assert schema_name in openapi["components"]["schemas"]

    def assert_research_error_ref(path: str, method: str, status_code: str) -> None:
        schema = response_schema(path, method, status_code)
        assert schema == {"$ref": "#/components/schemas/ResearchErrorResponse"}
        assert_ref_resolves(schema["$ref"])

    def assert_validation_error_ref(path: str, method: str, status_code: str) -> None:
        schema = response_schema(path, method, status_code)
        assert schema == {"$ref": "#/components/schemas/HTTPValidationError"}
        assert_ref_resolves(schema["$ref"])

    def assert_research_or_validation_one_of(
        path: str,
        method: str,
        status_code: str,
    ) -> None:
        schema = response_schema(path, method, status_code)
        one_of_refs = {item["$ref"] for item in schema["oneOf"]}
        assert one_of_refs == {
            "#/components/schemas/HTTPValidationError",
            "#/components/schemas/ResearchErrorResponse",
        }
        for ref in one_of_refs:
            assert_ref_resolves(ref)

    for path, method, status_code in {
        (base, "post", "404"),
        (base, "post", "409"),
        (f"{base}/current", "get", "404"),
        (f"{base}/versions/{{version}}", "get", "404"),
        (f"{base}/refresh", "post", "404"),
        (f"{base}/refresh", "post", "409"),
    }:
        assert_research_error_ref(path, method, status_code)

    assert_research_or_validation_one_of(base, "post", "422")
    assert_research_or_validation_one_of(f"{base}/refresh", "post", "422")
    assert_validation_error_ref(f"{base}/versions/{{version}}", "get", "422")
