"""Tests for Jinja2 template analysis."""

from pytest_jinja_check import (
    analyze_all_templates,
    analyze_template,
    check_hardcoded_routes,
    check_syntax,
)
from pytest_jinja_check.models import IssueCategory


class TestAnalyzeTemplate:
    def test_simple_template(self, templates_dir):
        info = analyze_template("partials/nav.html", templates_dir)
        assert info.name == "partials/nav.html"
        assert "nav_links" in info.variables
        assert info.parent_template is None

    def test_child_inherits_parent_variables(self, templates_dir):
        info = analyze_template("home.html", templates_dir)
        # 'title' comes from base.html, 'heading' and 'items' from home.html
        assert "title" in info.variables
        assert "heading" in info.variables
        assert "items" in info.variables
        assert info.parent_template == "base.html"

    def test_parent_url_for_calls_inherited(self, templates_dir):
        info = analyze_template("home.html", templates_dir)
        endpoints = [ep for ep, _line in info.url_for_calls]
        # base.html has url_for('home') and url_for('about')
        assert "home" in endpoints
        assert "about" in endpoints

    def test_child_url_for_calls_included(self, templates_dir):
        info = analyze_template("about.html", templates_dir)
        endpoints = [ep for ep, _line in info.url_for_calls]
        assert "nonexistent" in endpoints

    def test_base_template_variables(self, templates_dir):
        info = analyze_template("base.html", templates_dir)
        assert "title" in info.variables
        assert info.parent_template is None

    def test_macro_import_not_in_variables(self, templates_dir):
        info = analyze_template("uses_macro.html", templates_dir)
        assert "render_logo" not in info.variables
        # Real context variables should still be detected
        assert "heading" in info.variables
        assert "title" in info.variables  # inherited from base.html

    def test_set_variable_not_in_variables_with_inheritance(self, templates_dir):
        """{% set %} in a child block should not be reported as missing,
        even when the parent's default block uses the same variable name."""
        info = analyze_template("uses_set_in_child.html", templates_dir)
        assert "subtitle" not in info.variables
        # Real context variables should still be detected
        assert "title" in info.variables  # from parent, outside any block

    def test_aliased_macro_import_not_in_variables(self, templates_dir):
        info = analyze_template("uses_macro_alias.html", templates_dir)
        assert "logo" not in info.variables
        assert "render_logo" not in info.variables
        assert "title" in info.variables  # inherited from base.html


class TestAnalyzeAllTemplates:
    def test_finds_all_templates(self, templates_dir):
        results = analyze_all_templates(templates_dir)
        assert "base.html" in results
        assert "home.html" in results
        assert "about.html" in results
        assert "partials/nav.html" in results

    def test_skips_bad_syntax_gracefully(self, templates_dir):
        # bad_syntax.html should cause an error during analysis,
        # but analyze_all_templates should be tested via check_syntax
        results = analyze_all_templates(templates_dir)
        # We should still get results for valid templates
        assert "base.html" in results


class TestCheckSyntax:
    def test_finds_syntax_errors(self, templates_dir):
        errors = check_syntax(templates_dir)
        bad = [e for e in errors if "bad_syntax" in e.file]
        assert len(bad) == 1
        assert bad[0].category == IssueCategory.SYNTAX_ERROR

    def test_valid_templates_pass(self, templates_dir):
        errors = check_syntax(templates_dir)
        valid_errors = [e for e in errors if "bad_syntax" not in e.file]
        assert len(valid_errors) == 0


class TestCheckHardcodedRoutes:
    def test_finds_hardcoded_route(self, templates_dir):
        errors = check_hardcoded_routes(templates_dir)
        assert any(
            e.category == IssueCategory.HARDCODED_ROUTE and "/contact" in e.message
            for e in errors
        )

    def test_does_not_flag_url_for_expressions(self, templates_dir):
        errors = check_hardcoded_routes(templates_dir)
        # Only /contact should be flagged, not URLs inside {{ url_for(...) }}
        flagged_urls = [e.message for e in errors]
        assert all("/contact" in msg for msg in flagged_urls)

    def test_allows_external_urls(self, templates_dir):
        errors = check_hardcoded_routes(templates_dir)
        # No errors for http:// or # links
        assert not any("http" in e.message for e in errors)
