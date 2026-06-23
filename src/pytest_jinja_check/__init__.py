"""pytest-jinja-check: Lint and test Jinja2 templates used in FastAPI apps."""

from .config import LinterConfig, load_config
from .context_validation import check_context_variables
from .endpoint_validation import get_registered_endpoints, validate_url_for_references
from .lint_runner import format_lint_errors, import_app, run_all_checks
from .models import IssueCategory, LintError, RouteContext, TemplateInfo
from .route_analysis import extract_all_route_contexts, extract_route_contexts
from .template_analysis import (
    analyze_all_templates,
    analyze_template,
    check_hardcoded_routes,
    check_syntax,
)

__all__ = [
    "IssueCategory",
    "LintError",
    "LinterConfig",
    "RouteContext",
    "TemplateInfo",
    "analyze_all_templates",
    "analyze_template",
    "check_context_variables",
    "check_hardcoded_routes",
    "check_syntax",
    "extract_all_route_contexts",
    "extract_route_contexts",
    "format_lint_errors",
    "get_registered_endpoints",
    "import_app",
    "load_config",
    "run_all_checks",
    "validate_url_for_references",
]
