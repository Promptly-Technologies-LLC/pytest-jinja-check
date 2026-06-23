"""Tests for the pytest plugin fixtures."""

import shutil
from pathlib import Path

import pytest

from pytest_jinja_check.config import LinterConfig

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def linter_config(templates_dir, app_dir):
    """Config pointing at our test fixtures."""
    return LinterConfig(
        template_dir=str(templates_dir),
        python_dir=str(app_dir),
        root=Path("."),  # not used since we provide absolute paths
    )


class TestPluginFixtures:
    """Test the plugin fixtures work end-to-end using the fixture app."""

    def test_template_variables_fixture(self, templates_dir):
        from pytest_jinja_check import analyze_all_templates

        results = analyze_all_templates(templates_dir)
        assert "home.html" in results
        assert "title" in results["home.html"].variables

    def test_full_lint_pipeline(self, templates_dir, app_dir):
        """Simulate what a user would do with the plugin fixtures."""
        from pytest_jinja_check import (
            analyze_all_templates,
            check_hardcoded_routes,
            check_syntax,
        )
        from pytest_jinja_check.context_validation import check_context_variables
        from pytest_jinja_check.route_analysis import extract_all_route_contexts

        # Syntax check
        syntax_errors = check_syntax(templates_dir)
        bad_syntax = [e for e in syntax_errors if "bad_syntax" in e.file]
        assert len(bad_syntax) == 1

        # Hardcoded routes
        hardcoded = check_hardcoded_routes(templates_dir)
        assert any("/contact" in e.message for e in hardcoded)

        # Context variables
        routes = extract_all_route_contexts(app_dir)
        context_errors = check_context_variables(templates_dir, routes)
        # about route is missing 'title'
        assert any("about" in e.message and "title" in e.message for e in context_errors)


def _write_fixture_project(path: Path) -> None:
    """Copy minimal fixture app/templates into a pytester project directory."""
    shutil.copytree(FIXTURES_DIR / "templates", path / "templates")
    shutil.copytree(FIXTURES_DIR / "app", path / "app")


class TestAutoCheck:
    def test_auto_check_fails_session_with_lint_errors(self, pytester):
        pytester.makepyprojecttoml(
            """
            [tool.pytest-jinja-check]
            template_dir = "templates"
            python_dir = "app"
            auto_check = true
            """
        )
        _write_fixture_project(pytester.path)
        pytester.makeconftest("import sys\nsys.path.insert(0, '.')\n")

        result = pytester.runpytest()
        assert result.ret != 0
        output = result.stdout.str() + result.stderr.str()
        assert "Jinja template lint failed" in output
        assert "syntax_error" in output

    def test_auto_check_disabled_by_default(self, pytester):
        pytester.makepyprojecttoml(
            """
            [tool.pytest-jinja-check]
            template_dir = "templates"
            python_dir = "app"
            """
        )
        _write_fixture_project(pytester.path)
        pytester.makeconftest("import sys\nsys.path.insert(0, '.')\n")
        pytester.makepyfile(test_ok="def test_ok(): assert True")

        result = pytester.runpytest()
        result.assert_outcomes(passed=1)

    def test_jinja_check_flag_enables_lint(self, pytester):
        pytester.makepyprojecttoml(
            """
            [tool.pytest-jinja-check]
            template_dir = "templates"
            python_dir = "app"
            """
        )
        _write_fixture_project(pytester.path)
        pytester.makeconftest("import sys\nsys.path.insert(0, '.')\n")

        result = pytester.runpytest("--jinja-check")
        assert result.ret != 0
        output = result.stdout.str() + result.stderr.str()
        assert "Jinja template lint failed" in output

    def test_no_jinja_check_overrides_auto_check(self, pytester):
        pytester.makepyprojecttoml(
            """
            [tool.pytest-jinja-check]
            template_dir = "templates"
            python_dir = "app"
            auto_check = true
            """
        )
        _write_fixture_project(pytester.path)
        pytester.makeconftest("import sys\nsys.path.insert(0, '.')\n")
        pytester.makepyfile(test_ok="def test_ok(): assert True")

        result = pytester.runpytest("--no-jinja-check")
        result.assert_outcomes(passed=1)
