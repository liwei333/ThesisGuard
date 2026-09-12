"""Frontend tooling configuration regression tests."""

from pathlib import Path


def test_frontend_has_eslint_configuration() -> None:
    """The frontend lint gate should have an ESLint config to load."""
    eslint_config = Path("apps/web/.eslintrc.cjs")

    assert eslint_config.exists()
    contents = eslint_config.read_text(encoding="utf-8")
    assert "plugin:vue/vue3-recommended" in contents
    assert "@typescript-eslint/parser" in contents
