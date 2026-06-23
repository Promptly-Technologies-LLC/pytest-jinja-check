"""Pytest plugin providing fixtures for Jinja2 template linting."""

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from .config import LinterConfig, load_config
from .context_validation import check_context_variables
from .endpoint_validation import validate_url_for_references
from .lint_runner import format_lint_errors, run_all_checks
from .route_analysis import extract_all_route_contexts
from .template_analysis import (
    analyze_all_templates,
    check_hardcoded_routes,
    check_syntax,
)

if TYPE_CHECKING:
    from .models import LintError, RouteContext, TemplateInfo


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--template-lint-config",
        default=None,
        help="Path to directory containing pyproject.toml with "
        "[tool.pytest-jinja-check] config",
    )
    parser.addoption(
        "--jinja-check",
        action="store_true",
        default=False,
        help="Run Jinja template lint checks at session start",
    )
    parser.addoption(
        "--no-jinja-check",
        action="store_true",
        default=False,
        help="Skip Jinja template lint checks even when auto_check is enabled",
    )


def _resolve_linter_config(config: pytest.Config) -> LinterConfig:
    config_path = config.getoption("--template-lint-config")
    if config_path:
        return load_config(Path(config_path))
    return load_config(Path(config.rootpath))


def _is_jinja_check_enabled(config: pytest.Config) -> bool:
    if config.getoption("--no-jinja-check"):
        return False
    if config.getoption("--jinja-check"):
        return True
    return _resolve_linter_config(config).auto_check


def pytest_sessionstart(session: pytest.Session) -> None:
    config = session.config
    if not _is_jinja_check_enabled(config):
        return

    linter_config = _resolve_linter_config(config)
    try:
        errors = run_all_checks(linter_config)
    except Exception as exc:
        pytest.exit(f"Jinja template lint failed to run: {exc}", returncode=1)

    if errors:
        pytest.exit(format_lint_errors(errors), returncode=1)


@pytest.fixture(scope="session")
def template_linter_config(request: pytest.FixtureRequest) -> LinterConfig:
    """Resolved linter configuration from pyproject.toml."""
    return _resolve_linter_config(request.config)


@pytest.fixture(scope="session")
def template_variables(
    template_linter_config: LinterConfig,
) -> dict[str, "TemplateInfo"]:
    """Map of template name -> TemplateInfo with extracted variables."""
    tpl_dir = template_linter_config.root / template_linter_config.template_dir
    return analyze_all_templates(tpl_dir)


@pytest.fixture(scope="session")
def route_contexts(template_linter_config: LinterConfig) -> list["RouteContext"]:
    """All TemplateResponse calls found via AST analysis of Python sources."""
    py_dir = template_linter_config.root / template_linter_config.python_dir
    return extract_all_route_contexts(py_dir, template_linter_config.route_file_patterns)


@pytest.fixture(scope="session")
def template_syntax_errors(
    template_linter_config: LinterConfig,
) -> list["LintError"]:
    """Template syntax errors found during parsing."""
    tpl_dir = template_linter_config.root / template_linter_config.template_dir
    return check_syntax(tpl_dir)


@pytest.fixture(scope="session")
def hardcoded_routes(template_linter_config: LinterConfig) -> list["LintError"]:
    """Hardcoded route detections in templates."""
    tpl_dir = template_linter_config.root / template_linter_config.template_dir
    return check_hardcoded_routes(
        tpl_dir,
        allowed_url_prefixes=template_linter_config.allowed_url_prefixes,
        ignore_attrs=template_linter_config.hardcoded_route_ignore_attrs,
    )


@pytest.fixture(scope="session")
def missing_context_variables(
    template_linter_config: LinterConfig,
    route_contexts: list["RouteContext"],
) -> list["LintError"]:
    """Routes that don't pass all required template variables."""
    tpl_dir = template_linter_config.root / template_linter_config.template_dir
    return check_context_variables(
        tpl_dir,
        route_contexts,
        ignore_variables=template_linter_config.ignore_variables,
    )


@pytest.fixture
def validate_endpoints(template_linter_config: LinterConfig):
    """Factory fixture: pass a FastAPI app, get back LintErrors for invalid url_for refs.

    Usage::

        def test_endpoints(validate_endpoints):
            from myapp.main import app
            errors = validate_endpoints(app)
            assert not errors
    """
    tpl_dir = template_linter_config.root / template_linter_config.template_dir

    def _validate(app, ignore_endpoints=None):
        return validate_url_for_references(tpl_dir, app, ignore_endpoints)

    return _validate
