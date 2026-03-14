"""Tests for the pytest plugin fixtures."""

from pathlib import Path

import pytest

from pytest_jinja_check.config import LinterConfig


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
