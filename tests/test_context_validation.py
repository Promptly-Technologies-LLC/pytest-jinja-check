"""Tests for context variable validation."""

from pytest_jinja_check.context_validation import check_context_variables
from pytest_jinja_check.models import IssueCategory, RouteContext


class TestCheckContextVariables:
    def test_detects_missing_variables(self, templates_dir):
        routes = [
            RouteContext(
                template_name="about.html",
                context_keys={"request"},
                source_file="app.py",
                line=10,
                function_name="about",
            ),
        ]
        errors = check_context_variables(templates_dir, routes)
        assert len(errors) == 1
        assert errors[0].category == IssueCategory.MISSING_CONTEXT_VAR
        assert "title" in errors[0].message

    def test_passes_when_all_provided(self, templates_dir):
        routes = [
            RouteContext(
                template_name="home.html",
                context_keys={"request", "title", "heading", "items"},
                source_file="app.py",
                line=5,
                function_name="home",
            ),
        ]
        errors = check_context_variables(templates_dir, routes)
        assert len(errors) == 0

    def test_skips_dynamic_context(self, templates_dir):
        routes = [
            RouteContext(
                template_name="home.html",
                context_keys=set(),
                source_file="app.py",
                line=5,
                function_name="home",
                has_dynamic_context=True,
            ),
        ]
        errors = check_context_variables(templates_dir, routes)
        assert len(errors) == 0

    def test_reports_missing_template(self, templates_dir):
        routes = [
            RouteContext(
                template_name="nonexistent.html",
                context_keys={"request"},
                source_file="app.py",
                line=5,
                function_name="missing",
            ),
        ]
        errors = check_context_variables(templates_dir, routes)
        assert len(errors) == 1
        assert "not found" in errors[0].message

    def test_respects_ignore_variables(self, templates_dir):
        routes = [
            RouteContext(
                template_name="home.html",
                context_keys={"request"},
                source_file="app.py",
                line=5,
                function_name="home",
            ),
        ]
        # Ignore all the template's variables
        errors = check_context_variables(
            templates_dir,
            routes,
            ignore_variables={"request", "title", "heading", "items", "url_for"},
        )
        assert len(errors) == 0
