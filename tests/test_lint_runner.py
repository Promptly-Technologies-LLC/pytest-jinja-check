"""Tests for the lint orchestration layer."""

from pathlib import Path

import pytest

from pytest_jinja_check.config import LinterConfig
from pytest_jinja_check.lint_runner import (
    format_lint_errors,
    import_app,
    run_all_checks,
)
from pytest_jinja_check.models import IssueCategory


class TestImportApp:
    def test_imports_app_from_module_path(self, app_dir):
        import sys

        sys.path.insert(0, str(app_dir.parent))
        try:
            app = import_app("app.main:app")
            assert app.__class__.__name__ == "FastAPI"
        finally:
            sys.path.remove(str(app_dir.parent))


class TestRunAllChecks:
    def test_collects_syntax_hardcoded_and_context_errors(
        self, templates_dir, app_dir
    ):
        config = LinterConfig(
            template_dir=str(templates_dir),
            python_dir=str(app_dir),
            root=Path("."),
        )
        errors = run_all_checks(config)

        categories = {e.category for e in errors}
        assert IssueCategory.SYNTAX_ERROR in categories
        assert IssueCategory.HARDCODED_ROUTE in categories
        assert IssueCategory.MISSING_CONTEXT_VAR in categories

    def test_validates_endpoints_when_app_configured(
        self, templates_dir, app_dir
    ):
        pytest.importorskip("fastapi")
        import sys

        sys.path.insert(0, str(app_dir.parent))
        try:
            config = LinterConfig(
                template_dir=str(templates_dir),
                python_dir=str(app_dir),
                app="app.main:app",
                root=Path("."),
            )
            errors = run_all_checks(config)
        finally:
            sys.path.remove(str(app_dir.parent))

        assert any(e.category == IssueCategory.INVALID_ENDPOINT for e in errors)


class TestFormatLintErrors:
    def test_includes_error_count(self):
        from pytest_jinja_check.models import LintError

        errors = [
            LintError(
                category=IssueCategory.SYNTAX_ERROR,
                message="bad template",
                file="bad.html",
                line=1,
            )
        ]
        report = format_lint_errors(errors)
        assert "Jinja template lint failed" in report
        assert "1 error(s) found" in report
        assert "bad.html:1" in report
