"""Validate url_for() references against a live FastAPI app's route table."""

from pathlib import Path
from typing import TYPE_CHECKING

from .models import IssueCategory, LintError
from .template_analysis import analyze_all_templates

if TYPE_CHECKING:
    from fastapi import FastAPI


def _collect_endpoints_from_routes(routes) -> set[str]:
    """Recursively collect named endpoints from a route table."""
    endpoints: set[str] = set()
    for route in routes:
        name = getattr(route, "name", None)
        if name:
            endpoints.add(name)

        original_router = getattr(route, "original_router", None)
        if original_router is not None:
            endpoints |= _collect_endpoints_from_routes(original_router.routes)
        elif getattr(route, "routes", None):
            endpoints |= _collect_endpoints_from_routes(route.routes)

    return endpoints


def get_registered_endpoints(app: "FastAPI") -> set[str]:
    """Extract all named endpoints from a FastAPI app."""
    return _collect_endpoints_from_routes(app.routes)


def validate_url_for_references(
    template_dir: Path,
    app: "FastAPI",
    ignore_endpoints: set[str] | None = None,
) -> list[LintError]:
    """Check that all url_for() calls in templates reference real endpoints.

    Args:
        template_dir: Root templates directory
        app: A FastAPI application instance
        ignore_endpoints: Optional set of endpoint names to skip
    """
    if ignore_endpoints is None:
        ignore_endpoints = set()

    registered = get_registered_endpoints(app)
    templates = analyze_all_templates(template_dir)
    errors = []

    for name, info in templates.items():
        for endpoint, line in info.url_for_calls:
            if endpoint in ignore_endpoints:
                continue
            if endpoint not in registered:
                errors.append(
                    LintError(
                        category=IssueCategory.INVALID_ENDPOINT,
                        message=(
                            f'url_for("{endpoint}") references unknown endpoint '
                            f"— registered endpoints: {sorted(registered)}"
                        ),
                        file=name,
                        line=line,
                    )
                )

    return errors
