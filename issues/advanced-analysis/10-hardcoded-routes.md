---
title: Detect hardcoded routes and URLs
labels: enhancement, static-analysis
milestone: v0.3.0
priority: P1
---

## Description

Detect hardcoded URLs in templates and suggest using `url_for()` or framework-specific URL helpers instead.

## Problem

Hardcoded URLs break when routes change:

```html
<!-- Bad: Hardcoded URL -->
<a href="/profile/edit">Edit Profile</a>

<!-- Good: Generated URL -->
<a href="{{ url_for('edit_profile') }}">Edit Profile</a>
```

## User Story

**As a developer**, I want to be warned about hardcoded URLs in my templates so I can use `url_for()` instead and avoid broken links when routes change.

## Detection Rules

### Detect Hardcoded Paths

Match common patterns:
- `href="/..."`
- `src="/static/..."`
- `action="/form/submit"`
- `<form action="/..."`

### Exclude Valid Cases

Don't warn for:
- External URLs: `href="https://example.com"`
- Anchors: `href="#section"`
- `mailto:` and `tel:` links
- Data URLs: `href="data:..."`
- Template variables: `href="{{ url }}"`

## Implementation

### Regex Patterns

```python
import re
from pathlib import Path
from typing import List, Tuple

# Pattern for hardcoded routes
HARDCODED_ROUTE_PATTERN = re.compile(
    r'''
    (?:href|src|action)\s*=\s*  # Attribute name
    ["']                         # Opening quote
    (/[^"'#\s][^"']*)           # Path starting with /
    ["']                         # Closing quote
    ''',
    re.VERBOSE | re.IGNORECASE
)

# Exclusions
EXTERNAL_URL = re.compile(r'^https?://')
STATIC_FILE = re.compile(r'^/static/')
MEDIA_FILE = re.compile(r'^/media/')

def detect_hardcoded_routes(template_path: Path) -> List[Tuple[int, str, str]]:
    """
    Detect hardcoded routes in template.

    Args:
        template_path: Path to template file

    Returns:
        List of (line_number, route, suggestion) tuples

    Example:
        >>> detect_hardcoded_routes(Path("template.html"))
        [
            (15, '/profile/edit', 'Use url_for("edit_profile")'),
            (23, '/logout', 'Use url_for("logout")')
        ]
    """
    issues = []

    with open(template_path) as f:
        for line_num, line in enumerate(f, 1):
            matches = HARDCODED_ROUTE_PATTERN.findall(line)

            for route in matches:
                # Skip valid cases
                if should_skip_route(route):
                    continue

                suggestion = suggest_url_helper(route)
                issues.append((line_num, route, suggestion))

    return issues

def should_skip_route(route: str) -> bool:
    """Check if route should be skipped (valid hardcoding)."""
    if EXTERNAL_URL.match(route):
        return True
    if STATIC_FILE.match(route):
        return True  # Static files are often OK to hardcode
    if MEDIA_FILE.match(route):
        return True
    if route.startswith('#'):
        return True
    if route.startswith('mailto:'):
        return True
    if route.startswith('tel:'):
        return True
    return False

def suggest_url_helper(route: str) -> str:
    """
    Suggest proper URL helper based on route.

    Returns framework-appropriate suggestion.
    """
    # Try to infer route name from path
    # /profile/edit -> edit_profile
    # /users/123/delete -> delete_user

    parts = [p for p in route.strip('/').split('/') if not p.isdigit()]

    if len(parts) >= 2:
        # Reverse order for route name: /profile/edit -> edit_profile
        route_name = '_'.join(parts[::-1])
    elif parts:
        route_name = parts[0]
    else:
        route_name = "your_route_name"

    return f'Use url_for("{route_name}") or equivalent'
```

### CLI Integration

Add to `check` command:

```bash
jinja2-validator check ./templates --check-routes

# Output:
templates/profile.html:15: Hardcoded route '/profile/edit'
  Suggestion: Use url_for("edit_profile")

templates/profile.html:23: Hardcoded route '/logout'
  Suggestion: Use url_for("logout")

Found 2 hardcoded routes in 1 template
```

### JSON Output

```json
{
  "hardcoded_routes": [
    {
      "file": "templates/profile.html",
      "line": 15,
      "route": "/profile/edit",
      "suggestion": "Use url_for('edit_profile')"
    }
  ]
}
```

## Configuration

Allow ignoring certain patterns:

```toml
# .jinja2-validator.toml
[routes]
check_hardcoded = true

# Patterns to ignore (regex)
ignore_patterns = [
    "^/static/",
    "^/media/",
    "^/admin/",  # Django admin URLs are OK hardcoded
]

# Specific routes to ignore
ignore_routes = [
    "/",  # Homepage is often "/" and that's fine
    "/health",
]
```

## Framework-Specific Suggestions

### Flask

```python
def suggest_flask_url(route: str) -> str:
    return f"Use url_for('{infer_route_name(route)}')"
```

### Django

```python
def suggest_django_url(route: str) -> str:
    return f"Use {{% url '{infer_route_name(route)}' %}}"
```

### FastAPI

```python
def suggest_fastapi_url(route: str) -> str:
    return f"Use url_for('{infer_route_name(route)}')"
```

Auto-detect framework from project structure.

## Testing

### Test Cases

```python
def test_detect_simple_hardcoded_route():
    template = '<a href="/profile/edit">Edit</a>'
    issues = detect_hardcoded_routes_in_string(template)
    assert len(issues) == 1
    assert issues[0][1] == '/profile/edit'

def test_ignore_external_url():
    template = '<a href="https://example.com">Link</a>'
    issues = detect_hardcoded_routes_in_string(template)
    assert len(issues) == 0

def test_ignore_static_files():
    template = '<img src="/static/logo.png">'
    issues = detect_hardcoded_routes_in_string(template)
    assert len(issues) == 0

def test_ignore_anchor():
    template = '<a href="#section">Link</a>'
    issues = detect_hardcoded_routes_in_string(template)
    assert len(issues) == 0

def test_detect_form_action():
    template = '<form action="/submit">'
    issues = detect_hardcoded_routes_in_string(template)
    assert len(issues) == 1
```

## Acceptance Criteria

- [ ] Detects hardcoded routes in href, src, action attributes
- [ ] Ignores external URLs
- [ ] Ignores static/media files (configurable)
- [ ] Ignores anchors (#section)
- [ ] Ignores mailto: and tel: links
- [ ] Provides framework-specific suggestions
- [ ] Integrated into `check` command
- [ ] Configuration file support
- [ ] JSON output support
- [ ] Line numbers in output
- [ ] Framework auto-detection
- [ ] Comprehensive tests
- [ ] Documentation

## Future Enhancements

- [ ] Auto-fix mode (replace hardcoded routes)
- [ ] Learn from existing url_for() usage
- [ ] Validate that suggested route names exist
- [ ] Check for broken links
- [ ] Integration with route documentation

## Related Issues

- #2 (CLI Tool)
- #3 (Syntax Validation)

## References

- Flask: https://flask.palletsprojects.com/en/stable/api/#flask.url_for
- Django: https://docs.djangoproject.com/en/stable/ref/templates/builtins/#url
- FastAPI: https://fastapi.tiangolo.com/advanced/templates/#using-url_for
