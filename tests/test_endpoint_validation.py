"""Tests for endpoint validation."""

import pytest

from pytest_jinja_check.endpoint_validation import (
    get_registered_endpoints,
    validate_url_for_references,
)
from pytest_jinja_check.models import IssueCategory


@pytest.fixture
def sample_app():
    """Create a minimal FastAPI app for testing."""
    fastapi = pytest.importorskip("fastapi")

    app = fastapi.FastAPI()

    @app.get("/", name="home")
    async def home():
        pass

    @app.get("/about", name="about")
    async def about_page():
        pass

    return app


class TestGetRegisteredEndpoints:
    def test_finds_named_routes(self, sample_app):
        endpoints = get_registered_endpoints(sample_app)
        assert "home" in endpoints
        assert "about" in endpoints


class TestValidateUrlForReferences:
    def test_detects_invalid_endpoint(self, templates_dir, sample_app):
        errors = validate_url_for_references(templates_dir, sample_app)
        # about.html has url_for('nonexistent')
        invalid = [e for e in errors if e.category == IssueCategory.INVALID_ENDPOINT]
        assert any("nonexistent" in e.message for e in invalid)

    def test_valid_endpoints_pass(self, templates_dir, sample_app):
        errors = validate_url_for_references(templates_dir, sample_app)
        # home and about endpoints exist — only 'nonexistent' should be flagged
        flagged_endpoints = [
            e.message.split('"')[1]  # extract endpoint from url_for("X")
            for e in errors
        ]
        assert "home" not in flagged_endpoints
        assert "about" not in flagged_endpoints

    def test_ignore_endpoints(self, templates_dir, sample_app):
        errors = validate_url_for_references(
            templates_dir, sample_app, ignore_endpoints={"nonexistent"}
        )
        assert not any("nonexistent" in e.message for e in errors)
