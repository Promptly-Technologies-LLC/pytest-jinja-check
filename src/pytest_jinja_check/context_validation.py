"""Validate that routes pass all required context variables to templates."""

from pathlib import Path

from .models import IssueCategory, LintError, RouteContext, TemplateInfo
from .template_analysis import analyze_all_templates


def check_context_variables(
    template_dir: Path,
    route_contexts: list[RouteContext],
    ignore_variables: set[str] | None = None,
) -> list[LintError]:
    """Check that each TemplateResponse provides all variables the template needs.

    Args:
        template_dir: Root templates directory
        route_contexts: TemplateResponse calls extracted from Python source
        ignore_variables: Variables to ignore (e.g. framework-provided ones)
    """
    if ignore_variables is None:
        ignore_variables = {"request", "url_for", "get_flashed_messages"}

    templates = analyze_all_templates(template_dir)
    errors = []

    for route in route_contexts:
        template_info = templates.get(route.template_name)
        if template_info is None:
            errors.append(
                LintError(
                    category=IssueCategory.MISSING_CONTEXT_VAR,
                    message=(
                        f'Template "{route.template_name}" not found in {template_dir}'
                    ),
                    file=route.template_name,
                    line=route.line,
                    source_file=route.source_file,
                )
            )
            continue

        if route.has_dynamic_context:
            # Can't verify dynamic context — skip silently
            continue

        required = template_info.variables - ignore_variables
        provided = route.context_keys - ignore_variables
        missing = required - provided

        if missing:
            fn = route.function_name or "<unknown>"
            errors.append(
                LintError(
                    category=IssueCategory.MISSING_CONTEXT_VAR,
                    message=(
                        f'Route "{fn}" renders "{route.template_name}" '
                        f"but does not provide: {sorted(missing)}"
                    ),
                    file=route.template_name,
                    line=route.line,
                    source_file=route.source_file,
                )
            )

    return errors
