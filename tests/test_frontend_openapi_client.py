"""Frontend OpenAPI client generation and drift gate contract tests.

验证前端 OpenAPI 生成的类型安全和契约一致性：
1. 规范文件（openapi.json）与当前 FastAPI 应用同步
2. 生成的客户端包含完整的 Research 模型和操作
3. 类型系统拒绝无效的错误体（编译期 + 运行时双重验证）
4. API 外观层（client.ts）不重复 OpenAPI URL 或 schema 接口
5. base URL 不重复 /api/v1 前缀
6. 错误守卫函数正确识别合法/非法的错误响应体

部分测试通过临时 TypeScript 探针 + esbuild 编译 + node 执行来
在真实运行时验证类型守卫行为。
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from apps.api.main import create_app

WEB_ROOT = Path("apps/web")
CANONICAL_OPENAPI = WEB_ROOT / "openapi.json"
GENERATED_DIR = WEB_ROOT / "src/api/generated"
CLIENT_FACADE = WEB_ROOT / "src/api/client.ts"
PACKAGE_JSON = WEB_ROOT / "package.json"
MAKEFILE = Path("Makefile")
SMOKE_MODULE = WEB_ROOT / "src/api/generated-client-smoke.ts"
GENERATED_API_ERROR = GENERATED_DIR / "core/ApiError.ts"
GENERATED_API_RESULT = GENERATED_DIR / "core/ApiResult.ts"
GENERATED_OPENAPI = GENERATED_DIR / "core/OpenAPI.ts"
GENERATED_REQUEST = GENERATED_DIR / "core/request.ts"

RESEARCH_PATHS = {
    "/api/v1/research/instruments/{instrument_id}/packages": {"get", "post"},
    "/api/v1/research/instruments/{instrument_id}/packages/current": {"get"},
    "/api/v1/research/instruments/{instrument_id}/packages/versions/{version}": {"get"},
    "/api/v1/research/instruments/{instrument_id}/packages/refresh": {"post"},
}
RESEARCH_MODELS = {
    "ResearchRefreshRequest",
    "ResearchPackageRead",
    "ResearchModuleRead",
    "ResearchErrorCode",
    "ResearchErrorDetail",
    "ResearchErrorResponse",
    "ResearchFreshness",
    "ResearchModuleType",
    "HTTPValidationError",
    "ValidationError",
}
BUSINESS_ENDPOINT_PATTERNS = (
    r"['\"]/health",
    r"['\"]/system/status",
    r"['\"]/tasks/",
    r"['\"]/instruments/",
    r"['\"]/watchlist",
    r"['\"]/research/",
)
HANDWRITTEN_OPENAPI_INTERFACE_PATTERN = re.compile(
    r"export\s+interface\s+("
    r"HealthResponse|SystemStatusResponse|TaskDispatchResponse|Instrument|"
    r"WatchlistItem|ResearchRefreshRequest|ResearchPackageRead|ResearchModuleRead|"
    r"ResearchErrorResponse|ResearchErrorDetail"
    r")\b"
)


def normalized_json(value: dict[str, Any]) -> str:
    """Return deterministic JSON for OpenAPI drift comparisons."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def response_schema(openapi: dict[str, Any], path: str, method: str, status_code: str) -> dict:
    return openapi["paths"][path][method]["responses"][status_code]["content"][
        "application/json"
    ]["schema"]


def collect_generated_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(GENERATED_DIR.rglob("*.ts"))
        if path.is_file()
    )


def test_canonical_openapi_artifact_matches_current_fastapi_app() -> None:
    """Canonical frontend OpenAPI artifact must be current app.openapi()."""
    assert CANONICAL_OPENAPI.exists(), "apps/web/openapi.json is missing"

    expected = create_app().openapi()
    actual = json.loads(CANONICAL_OPENAPI.read_text(encoding="utf-8"))

    assert normalized_json(actual) == normalized_json(expected)


def test_frontend_api_generation_gates_are_declared() -> None:
    """NPM and Makefile drift gates must be non-interactive and discoverable."""
    package_json = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
    scripts = package_json["scripts"]
    makefile = MAKEFILE.read_text(encoding="utf-8")

    missing = [
        script
        for script in ("api:generate", "api:check", "typecheck", "build")
        if script not in scripts
    ]
    assert not missing
    assert "frontend-api-generate:" in makefile
    assert "frontend-api-check:" in makefile
    assert "frontend-check:" in makefile and "frontend-api-check" in makefile
    assert package_json["devDependencies"]["openapi-typescript-codegen"] == "0.29.0"


def test_generated_client_contains_research_contract_and_operations() -> None:
    """Generated output must contain complete Research models and callable operations."""
    assert GENERATED_DIR.exists(), "generated API client directory is missing"

    generated_files = sorted(path for path in GENERATED_DIR.rglob("*.ts") if path.is_file())
    assert generated_files, "generated API client contains no TypeScript files"
    banned_marker = "place" + "holder"
    assert all(banned_marker not in path.read_text(encoding="utf-8").lower() for path in generated_files)

    generated_text = collect_generated_text()
    for model_name in RESEARCH_MODELS:
        assert model_name in generated_text

    for operation_fragment in (
        "createInitialResearchPackage",
        "getCurrentResearchPackage",
        "listResearchPackageHistory",
        "getResearchPackageVersion",
        "refreshResearchPackage",
    ):
        assert operation_fragment in generated_text

    assert "idempotencyKey" in generated_text
    assert "ResearchFreshness" in generated_text
    assert "UNVERIFIED" in generated_text
    assert "FAILED" in generated_text


def test_generated_typescript_files_end_with_one_newline() -> None:
    """Generated files must pass Git's staged whitespace integrity gate."""
    generated_files = sorted(path for path in GENERATED_DIR.rglob("*.ts") if path.is_file())

    invalid_files = [
        str(path)
        for path in generated_files
        if not path.read_bytes().endswith(b"\n") or path.read_bytes().endswith(b"\n\n")
    ]

    assert not invalid_files, f"generated files have invalid EOF whitespace: {invalid_files}"


def test_generated_error_core_and_facade_expose_typed_research_failures() -> None:
    """Research failures must be typed on the real generated/facade boundary."""
    api_error = GENERATED_API_ERROR.read_text(encoding="utf-8")
    api_result = GENERATED_API_RESULT.read_text(encoding="utf-8")
    openapi_config = GENERATED_OPENAPI.read_text(encoding="utf-8")
    request_core = GENERATED_REQUEST.read_text(encoding="utf-8")
    client_source = CLIENT_FACADE.read_text(encoding="utf-8")
    smoke_source = SMOKE_MODULE.read_text(encoding="utf-8")

    assert "export class ApiError<TBody = unknown>" in api_error
    assert "public readonly body: TBody" in api_error
    assert "readonly body: TBody" in api_result
    assert "body: any" not in api_error
    assert "body: any" not in api_result

    assert "AXIOS?: AxiosInstance" in openapi_config
    assert "config.AXIOS ?? axios" in request_core
    assert "export const apiClient: AxiosInstance = axios.create" in client_source
    assert "export { OpenAPI as openApiConfig }" in client_source
    assert "export { OpenAPI as apiClient }" not in client_source

    assert "type ResearchErrorContract" in client_source
    assert "ResearchApiErrorBodyForStatus<'createInitial', 422>" in smoke_source
    assert "ResearchApiErrorBodyForStatus<'refresh', 422>" in smoke_source
    assert "ResearchApiErrorBodyForStatus<'getVersion', 422>" in smoke_source
    assert "type IsAny<T>" in smoke_source
    assert "const compatibleClient: AxiosInstance = apiClient" in smoke_source
    assert "acceptResearchOrValidationError" not in smoke_source


def test_research_openapi_contract_is_preserved_for_client_generation() -> None:
    """Research OpenAPI schemas must retain the contract required by the generated client."""
    openapi = json.loads(CANONICAL_OPENAPI.read_text(encoding="utf-8"))
    components = openapi["components"]["schemas"]

    for path, methods in RESEARCH_PATHS.items():
        assert path in openapi["paths"]
        assert methods.issubset(openapi["paths"][path])

    assert RESEARCH_MODELS.issubset(components)
    assert components["ResearchFreshness"]["enum"] == [
        "UNVERIFIED",
        "FRESH",
        "STALE",
        "FAILED",
    ]

    create_params = openapi["paths"][
        "/api/v1/research/instruments/{instrument_id}/packages"
    ]["post"]["parameters"]
    refresh_params = openapi["paths"][
        "/api/v1/research/instruments/{instrument_id}/packages/refresh"
    ]["post"]["parameters"]
    for params in (create_params, refresh_params):
        idempotency = next(param for param in params if param["name"] == "Idempotency-Key")
        assert idempotency["in"] == "header"
        assert idempotency["required"] is True

    expected_one_of = {
        "#/components/schemas/HTTPValidationError",
        "#/components/schemas/ResearchErrorResponse",
    }
    for path in (
        "/api/v1/research/instruments/{instrument_id}/packages",
        "/api/v1/research/instruments/{instrument_id}/packages/refresh",
    ):
        refs = {item["$ref"] for item in response_schema(openapi, path, "post", "422")["oneOf"]}
        assert refs == expected_one_of

    version_422 = response_schema(
        openapi,
        "/api/v1/research/instruments/{instrument_id}/packages/versions/{version}",
        "get",
        "422",
    )
    assert version_422 == {"$ref": "#/components/schemas/HTTPValidationError"}


def test_api_facade_is_thin_and_generated_files_are_tracked() -> None:
    """Manual API boundary should not duplicate OpenAPI URLs or schema interfaces."""
    client_source = CLIENT_FACADE.read_text(encoding="utf-8")
    violations = [
        pattern
        for pattern in BUSINESS_ENDPOINT_PATTERNS
        if re.search(pattern, client_source)
    ]

    assert not violations
    assert not HANDWRITTEN_OPENAPI_INTERFACE_PATTERN.search(client_source)
    assert SMOKE_MODULE.exists()

    check_ignore = subprocess.run(
        ["git", "check-ignore", "-q", "--no-index", str(GENERATED_DIR / "index.ts")],
        check=False,
    )
    assert check_ignore.returncode == 1


def test_api_base_url_does_not_duplicate_api_version_prefix() -> None:
    """Generated paths already include /api/v1, so base URL must not append it."""
    client_source = CLIENT_FACADE.read_text(encoding="utf-8")
    generated_research = GENERATED_DIR.joinpath("services/ResearchService.ts").read_text(
        encoding="utf-8"
    )

    assert "VITE_API_VERSION" not in client_source
    assert "/api/v1" not in client_source
    assert "url: '/api/v1/research/instruments/{instrument_id}/packages'" in generated_research

    generated_path = "/api/v1/health"

    def final_url(base_url: str | None) -> str:
        base = (base_url or "").rstrip("/")
        return f"{base}{generated_path}"

    assert final_url(None) == "/api/v1/health"
    assert final_url("") == "/api/v1/health"
    assert final_url("http://localhost:8000") == "http://localhost:8000/api/v1/health"
    assert (
        final_url("http://localhost:8000/")
        == "http://localhost:8000/api/v1/health"
    )
    assert "/api/v1/api/v1" not in final_url("http://localhost:8000")


def test_generated_api_error_status_logging_uses_real_facade_path() -> None:
    """A generated ApiError must log its HTTP status and still propagate."""
    web_root = WEB_ROOT.resolve()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        probe = temp_path / "api-logging-probe.ts"
        bundled = temp_path / "api-logging-probe.cjs"
        probe.write_text(
            f"""
import {{
  ApiError,
  ResearchErrorCode,
  type ApiResult,
  type ResearchErrorResponse,
}} from {json.dumps(str(web_root / "src/api/generated/index.ts"))}
import {{
  reportApiErrorAndRethrow,
}} from {json.dumps(str(web_root / "src/api/client.ts"))}

const body: ResearchErrorResponse = {{
  detail: {{
    code: ResearchErrorCode.IDEMPOTENCY_CONFLICT,
    message: 'conflict',
  }},
}}
const result: ApiResult<ResearchErrorResponse> = {{
  url: '/api/v1/research/instruments/example/packages',
  ok: false,
  status: 409,
  statusText: 'Conflict',
  body,
}}
const generatedError = new ApiError<ResearchErrorResponse>(
  {{ method: 'POST', url: '/api/v1/research/instruments/{{instrument_id}}/packages' }},
  result,
  'Research conflict',
)
const captured: unknown[][] = []
const originalConsoleError = console.error
console.error = (...args: unknown[]) => {{
  captured.push(args)
}}
try {{
  reportApiErrorAndRethrow(generatedError)
  throw new Error('expected reportApiErrorAndRethrow to throw')
}} catch (error) {{
  if (error !== generatedError) {{
    throw new Error('reported error was not rethrown')
  }}
}} finally {{
  console.error = originalConsoleError
}}
if (captured.length !== 1) {{
  throw new Error(`expected one log entry, got ${{captured.length}}`)
}}
if (captured[0][1] !== 409) {{
  throw new Error(`expected logged status 409, got ${{String(captured[0][1])}}`)
}}
""",
            encoding="utf-8",
        )
        build = subprocess.run(
            [
                "node_modules/.bin/esbuild",
                str(probe),
                "--bundle",
                "--platform=node",
                "--format=cjs",
                "--define:import.meta.env.VITE_API_BASE_URL=undefined",
                f"--outfile={bundled}",
            ],
            cwd=WEB_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert build.returncode == 0, build.stderr

        run = subprocess.run(
            ["node", str(bundled)],
            text=True,
            capture_output=True,
            check=False,
        )
        assert run.returncode == 0, run.stderr


def test_research_error_type_guards_match_generated_runtime_schemas() -> None:
    """Public Research error guards must not narrow malformed unknown bodies."""
    web_root = WEB_ROOT.resolve()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        probe = temp_path / "research-guard-probe.ts"
        bundled = temp_path / "research-guard-probe.cjs"
        probe.write_text(
            f"""
import {{
  ApiError,
  ResearchErrorCode,
  type ApiResult,
  type ResearchErrorResponse,
}} from {json.dumps(str(web_root / "src/api/generated/index.ts"))}
import {{
  isResearchApiError,
  isResearchApiErrorForStatus,
}} from {json.dumps(str(web_root / "src/api/client.ts"))}

function buildApiError(status: number, body: unknown): ApiError<unknown> {{
  const result: ApiResult<unknown> = {{
    url: '/api/v1/research/instruments/example/packages',
    ok: false,
    status,
    statusText: String(status),
    body,
  }}
  return new ApiError<unknown>(
    {{
      method: 'POST',
      url: '/api/v1/research/instruments/{{instrument_id}}/packages',
    }},
    result,
    'Research error',
  )
}}

const failures: string[] = []

function expectGuard(label: string, actual: boolean, expected: boolean): void {{
  if (actual !== expected) {{
    failures.push(`${{label}} expected ${{expected}} but got ${{actual}}`)
  }}
}}

const validResearchError: ResearchErrorResponse = {{
  detail: {{
    code: ResearchErrorCode.RESEARCH_VERSION_CONFLICT,
    message: 'version conflict',
    expected_version: 2,
    current_version: null,
  }},
}}

expectGuard(
  'valid research 409 status guard',
  isResearchApiErrorForStatus(buildApiError(409, validResearchError), 'refresh', 409),
  true,
)
expectGuard(
  'valid research generic guard',
  isResearchApiError(buildApiError(409, validResearchError), 'refresh'),
  true,
)
expectGuard(
  'valid create 422 research body',
  isResearchApiErrorForStatus(buildApiError(422, validResearchError), 'createInitial', 422),
  true,
)
expectGuard(
  'valid validation body',
  isResearchApiErrorForStatus(
    buildApiError(422, {{
      detail: [
        {{
          loc: ['body', 'expected_version', 0],
          msg: 'Input should be a valid integer',
          type: 'int_parsing',
        }},
      ],
    }}),
    'getVersion',
    422,
  ),
  true,
)
expectGuard(
  'generated HTTPValidationError optional detail',
  isResearchApiErrorForStatus(buildApiError(422, {{}}), 'getVersion', 422),
  true,
)
expectGuard(
  'unknown research error code',
  isResearchApiErrorForStatus(
    buildApiError(409, {{
      detail: {{
        code: 'NOT_A_RESEARCH_ERROR_CODE',
        message: 'not generated',
      }},
    }}),
    'refresh',
    409,
  ),
  false,
)
expectGuard(
  'invalid expected_version type',
  isResearchApiErrorForStatus(
    buildApiError(409, {{
      detail: {{
        code: ResearchErrorCode.RESEARCH_VERSION_CONFLICT,
        message: 'bad version field',
        expected_version: '2',
      }},
    }}),
    'refresh',
    409,
  ),
  false,
)
expectGuard(
  'invalid current_version type',
  isResearchApiErrorForStatus(
    buildApiError(409, {{
      detail: {{
        code: ResearchErrorCode.RESEARCH_VERSION_CONFLICT,
        message: 'bad version field',
        current_version: {{ value: 2 }},
      }},
    }}),
    'refresh',
    409,
  ),
  false,
)
expectGuard(
  'invalid validation loc object item',
  isResearchApiErrorForStatus(
    buildApiError(422, {{
      detail: [
        {{
          loc: ['body', {{ field: 'expected_version' }}],
          msg: 'Input should be a valid integer',
          type: 'int_parsing',
        }},
      ],
    }}),
    'getVersion',
    422,
  ),
  false,
)
expectGuard(
  'invalid validation loc boolean item',
  isResearchApiErrorForStatus(
    buildApiError(422, {{
      detail: [
        {{
          loc: ['body', true],
          msg: 'Input should be a valid integer',
          type: 'int_parsing',
        }},
      ],
    }}),
    'getVersion',
    422,
  ),
  false,
)
expectGuard(
  'missing validation required field',
  isResearchApiErrorForStatus(
    buildApiError(422, {{
      detail: [
        {{
          loc: ['body'],
          msg: 'field required',
        }},
      ],
    }}),
    'getVersion',
    422,
  ),
  false,
)
expectGuard(
  'research body is not valid for version 422',
  isResearchApiErrorForStatus(buildApiError(422, validResearchError), 'getVersion', 422),
  false,
)
if (failures.length > 0) {{
  throw new Error(failures.join('\\n'))
}}
""",
            encoding="utf-8",
        )
        build = subprocess.run(
            [
                "node_modules/.bin/esbuild",
                str(probe),
                "--bundle",
                "--platform=node",
                "--format=cjs",
                "--define:import.meta.env.VITE_API_BASE_URL=undefined",
                f"--outfile={bundled}",
            ],
            cwd=WEB_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert build.returncode == 0, build.stderr

        run = subprocess.run(
            ["node", str(bundled)],
            text=True,
            capture_output=True,
            check=False,
        )
        assert run.returncode == 0, run.stderr
