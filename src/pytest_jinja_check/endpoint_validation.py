"""Validate url_for() references against a live FastAPI app's route table."""

from pathlib import Path
from typing import TYPE_CHECKING

from .models import IssueCategory, LintError
from .template_analysis import analyze_all_templates

if TYPE_CHECKING:
    from fastapi import FastAPI


def get_registered_endpoints(app: "FastAPI") -> set[str]:
    """Extract all named endpoints from a FastAPI app."""
    endpoints = set()
    for route in app.routes:
        name = getattr(route, "name", None)
        if name:
            endpoints.add(name)
    return endpoints


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
