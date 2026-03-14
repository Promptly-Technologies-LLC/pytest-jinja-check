"""Jinja2 template analysis: variable extraction, url_for detection, syntax checks."""

import re
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError, meta, nodes

from .models import IssueCategory, LintError, TemplateInfo


def _create_env(template_dir: Path) -> Environment:
    """Create a Jinja2 environment with a filesystem loader."""
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True,
    )


def _get_parent_template(ast: nodes.Template) -> Optional[str]:
    """Extract the parent template name from an extends node."""
    for node in ast.find_all(nodes.Extends):
        if isinstance(node.template, nodes.Const):
            return node.template.value
    return None


def _extract_url_for_calls(ast: nodes.Template) -> list[tuple[str, int]]:
    """Extract url_for('endpoint') calls from a template AST.

    Returns list of (endpoint_name, line_number).
    """
    calls = []
    for node in ast.find_all(nodes.Call):
        if isinstance(node.node, nodes.Name) and node.node.name == "url_for":
            if node.args and isinstance(node.args[0], nodes.Const):
                calls.append((node.args[0].value, node.lineno))
    return calls


def analyze_template(
    template_name: str,
    template_dir: Path,
    env: Optional[Environment] = None,
    _seen: Optional[set] = None,
) -> TemplateInfo:
    """Analyze a single template, resolving inheritance for variables.

    Args:
        template_name: Relative template path (e.g. "home.html")
        template_dir: Root templates directory
        env: Optional pre-created Jinja2 Environment
        _seen: Internal set to prevent infinite recursion on circular extends
    """
    if env is None:
        env = _create_env(template_dir)
    if _seen is None:
        _seen = set()

    if template_name in _seen:
        # Circular extends — return empty to avoid infinite loop
        return TemplateInfo(
            name=template_name,
            source_path=template_dir / template_name,
        )
    _seen.add(template_name)

    source_path = template_dir / template_name
    source = source_path.read_text()
    ast = env.parse(source)

    variables = meta.find_undeclared_variables(ast)
    parent_name = _get_parent_template(ast)
    url_for_calls = _extract_url_for_calls(ast)

    # Merge parent template's variables (inheritance)
    if parent_name:
        parent_info = analyze_template(parent_name, template_dir, env, _seen)
        variables = variables | parent_info.variables
        url_for_calls = parent_info.url_for_calls + url_for_calls

    return TemplateInfo(
        name=template_name,
        source_path=source_path,
        variables=variables,
        parent_template=parent_name,
        url_for_calls=url_for_calls,
    )


def analyze_all_templates(
    template_dir: Path,
) -> dict[str, TemplateInfo]:
    """Analyze all HTML templates in a directory tree.

    Templates with syntax errors are silently skipped (use check_syntax to find them).
    """
    template_dir = Path(template_dir)
    env = _create_env(template_dir)
    results = {}

    for path in sorted(template_dir.rglob("*.html")):
        name = str(path.relative_to(template_dir))
        try:
            results[name] = analyze_template(name, template_dir, env)
        except TemplateSyntaxError:
            pass

    return results


def check_syntax(template_dir: Path) -> list[LintError]:
    """Validate Jinja2 syntax for all templates."""
    template_dir = Path(template_dir)
    env = _create_env(template_dir)
    errors = []

    for path in sorted(template_dir.rglob("*.html")):
        name = str(path.relative_to(template_dir))
        try:
            source = path.read_text()
            env.parse(source)
        except TemplateSyntaxError as e:
            errors.append(
                LintError(
                    category=IssueCategory.SYNTAX_ERROR,
                    message=str(e),
                    file=name,
                    line=e.lineno,
                )
            )

    return errors


# Regex to find hardcoded routes in HTML attributes.
# Matches href="/...", action="/...", formaction="/..."
_HARDCODED_ROUTE_RE = re.compile(
    r"""(?:href|action|formaction)\s*=\s*["'](/[^"']*?)["']""",
    re.IGNORECASE,
)

# Regex to detect if we're inside a Jinja2 expression {{ ... }}
_JINJA_EXPR_RE = re.compile(r"\{\{.*?\}\}", re.DOTALL)


def check_hardcoded_routes(
    template_dir: Path,
    allowed_url_prefixes: Optional[list[str]] = None,
    ignore_attrs: Optional[set[str]] = None,
) -> list[LintError]:
    """Find hardcoded routes in templates that should use url_for()."""
    if allowed_url_prefixes is None:
        allowed_url_prefixes = ["#", "http://", "https://", "mailto:", "tel:"]
    if ignore_attrs is None:
        ignore_attrs = {"src", "poster", "data"}

    template_dir = Path(template_dir)
    errors = []

    for path in sorted(template_dir.rglob("*.html")):
        name = str(path.relative_to(template_dir))
        source = path.read_text()

        # Find all Jinja2 expression spans so we can exclude matches inside them
        jinja_spans = [
            (m.start(), m.end()) for m in _JINJA_EXPR_RE.finditer(source)
        ]

        for match in _HARDCODED_ROUTE_RE.finditer(source):
            url = match.group(1)

            # Skip allowed prefixes
            if any(url.startswith(prefix) for prefix in allowed_url_prefixes):
                continue

            # Skip if this match is inside a Jinja2 expression
            pos = match.start()
            if any(start <= pos < end for start, end in jinja_spans):
                continue

            # Calculate line number
            line = source[:pos].count("\n") + 1

            errors.append(
                LintError(
                    category=IssueCategory.HARDCODED_ROUTE,
                    message=f'Hardcoded route "{url}" — use url_for() instead',
                    file=name,
                    line=line,
                )
            )

    return errors
