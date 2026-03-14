# pytest-jinja-check

A pytest plugin that lints Jinja2 templates used in FastAPI applications. Catches common issues at test time:

1. **Syntax validation** — templates parse without errors
2. **Hardcoded route detection** — `href="/foo"` should be `url_for('foo')`
3. **Endpoint validation** — `url_for('endpoint')` references actually exist in your app
4. **Context variable checking** — routes pass all variables their templates need

## Installation

```bash
pip install pytest-jinja-check
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add pytest-jinja-check
```

For endpoint validation against a live FastAPI app, install with the `fastapi` extra:

```bash
pip install "pytest-jinja-check[fastapi]"
# or
uv add "pytest-jinja-check[fastapi]"
```

## Quick start

The plugin auto-registers with pytest via entry points. Add configuration to your `pyproject.toml`:

```toml
[tool.pytest-jinja-check]
template_dir = "templates"
python_dir = "app"
```

Then write tests using the provided fixtures:

```python
# tests/test_templates.py

def test_template_syntax(template_syntax_errors):
    assert not template_syntax_errors, "\n".join(str(e) for e in template_syntax_errors)

def test_no_hardcoded_routes(hardcoded_routes):
    assert not hardcoded_routes, "\n".join(str(e) for e in hardcoded_routes)

def test_context_variables(missing_context_variables):
    assert not missing_context_variables, "\n".join(
        str(e) for e in missing_context_variables
    )

def test_url_for_endpoints(validate_endpoints):
    from myapp.main import app
    errors = validate_endpoints(app)
    assert not errors, "\n".join(str(e) for e in errors)
```

Run your tests as usual:

```bash
pytest
```

## Fixtures

All analysis fixtures are **session-scoped** (run once per test session).

| Fixture | Returns | Description |
| --- | --- | --- |
| `template_linter_config` | `LinterConfig` | Resolved configuration |
| `template_variables` | `dict[str, TemplateInfo]` | Template name -> extracted variables (with inheritance) |
| `route_contexts` | `list[RouteContext]` | All `TemplateResponse` calls found via AST |
| `template_syntax_errors` | `list[LintError]` | Templates that fail to parse |
| `hardcoded_routes` | `list[LintError]` | Hardcoded URLs that should use `url_for()` |
| `missing_context_variables` | `list[LintError]` | Routes missing required template variables |
| `validate_endpoints` | `callable(app) -> list[LintError]` | Factory: validates `url_for()` refs against a live app |

## Configuration

All settings in `[tool.pytest-jinja-check]` in your `pyproject.toml`:

| Key | Default | Description |
| --- | --- | --- |
| `template_dir` | `"templates"` | Template directory relative to project root |
| `python_dir` | `"."` | Directory to scan for Python route files |
| `route_file_patterns` | `["**/*.py"]` | Glob patterns for route files |
| `ignore_variables` | `["request", "url_for", ...]` | Variables to skip (framework-provided) |
| `allowed_url_prefixes` | `["#", "http://", ...]` | URL prefixes that aren't hardcoded routes |

You can also pass `--template-lint-config <path>` to pytest to specify a different directory containing `pyproject.toml`.

## Programmatic API

The analysis functions can also be used outside of pytest:

```python
from pytest_jinja_check import (
    analyze_all_templates,
    check_syntax,
    check_hardcoded_routes,
    check_context_variables,
    validate_url_for_references,
    extract_all_route_contexts,
)
from pathlib import Path

# Analyze templates
templates = analyze_all_templates(Path("templates"))
for name, info in templates.items():
    print(f"{name}: needs {info.variables}")

# Find issues
syntax_errors = check_syntax(Path("templates"))
hardcoded = check_hardcoded_routes(Path("templates"))
routes = extract_all_route_contexts(Path("app"))
missing = check_context_variables(Path("templates"), routes)
```

## How it works

- **Template analysis** uses `jinja2.meta.find_undeclared_variables()` on parsed ASTs, recursively resolving `{% extends %}` to capture inherited variable requirements.
- **Route analysis** uses Python's `ast` module to find `TemplateResponse(...)` calls and extract template names and context dict keys. Handles both the old positional API and newer keyword API.
- **Endpoint validation** introspects a live FastAPI `app.routes` to get registered endpoint names.

### Known limitations

- Template variables from dynamic `{% extends variable %}` can't be resolved.
- Context dicts built outside the `TemplateResponse(...)` call (e.g., `ctx = {...}; TemplateResponse("t.html", ctx)`) are flagged as dynamic and skipped rather than producing false positives.
- The variable union from template inheritance may over-report when a child block completely replaces a parent block that used a variable.

## License

MIT
