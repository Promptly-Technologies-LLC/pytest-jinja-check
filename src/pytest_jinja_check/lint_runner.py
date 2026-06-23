"""Orchestrate all template lint checks for automatic pytest runs."""

import importlib

from .config import LinterConfig
from .context_validation import check_context_variables
from .endpoint_validation import validate_url_for_references
from .models import LintError
from .route_analysis import extract_all_route_contexts
from .template_analysis import (
    analyze_all_templates,
    check_hardcoded_routes,
    check_syntax,
)


def import_app(import_path: str):
    """Import an application object from a ``module:attr`` string."""
    if ":" not in import_path:
        raise ValueError(
            f'App import string must be "module:attr", got "{import_path}"'
        )
    module_name, attr_name = import_path.rsplit(":", 1)
    module = importlib.import_module(module_name)
    return getattr(module, attr_name)


def run_all_checks(config: LinterConfig) -> list[LintError]:
    """Run syntax, route, context, and optional endpoint checks."""
    tpl_dir = config.root / config.template_dir
    py_dir = config.root / config.python_dir

    errors: list[LintError] = []
    errors.extend(check_syntax(tpl_dir))
    errors.extend(
        check_hardcoded_routes(
            tpl_dir,
            allowed_url_prefixes=config.allowed_url_prefixes,
            ignore_attrs=config.hardcoded_route_ignore_attrs,
        )
    )

    route_contexts = extract_all_route_contexts(
        py_dir, config.route_file_patterns
    )
    templates = analyze_all_templates(tpl_dir)
    errors.extend(
        check_context_variables(
            tpl_dir,
            route_contexts,
            ignore_variables=config.ignore_variables,
            templates=templates,
        )
    )

    if config.app:
        app = import_app(config.app)
        errors.extend(
            validate_url_for_references(tpl_dir, app, templates=templates)
        )

    return errors


def format_lint_errors(errors: list[LintError]) -> str:
    """Format lint errors for pytest exit output."""
    lines = ["Jinja template lint failed:", ""]
    for error in errors:
        lines.append(str(error))
    lines.extend(["", f"{len(errors)} error(s) found."])
    return "\n".join(lines)
