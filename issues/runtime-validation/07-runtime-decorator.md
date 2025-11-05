---
title: Implement runtime context validation decorator
labels: enhancement, runtime-validation
milestone: v0.2.0
priority: P0
---

## Description

Create a decorator that validates template context at runtime, ensuring all required variables are provided before rendering. **This is the killer feature that sets us apart from other tools.**

## User Story

**As a FastAPI/Flask developer**, I want to be notified immediately when I forget to pass a required variable to a template, so I can fix it before it reaches production.

## Current Problem

```python
# This code has a bug but won't fail until the template renders
@app.get("/profile")
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": user.name
        # BUG: Missing 'email' variable that template requires!
    })
```

## Proposed Solution

```python
from jinja2_validator import validate_template

@app.get("/profile")
@validate_template("profile.html")
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": user.name
        # ^ Error raised immediately: "Missing required variable 'email'"
    })
```

## API Design

### Basic Decorator

```python
@validate_template(template_name: str, strict: bool = True, ignore: List[str] = None)
```

**Parameters:**
- `template_name`: Path to template file (relative to template directory)
- `strict`: If True, raise exception on missing vars. If False, log warning.
- `ignore`: List of variable names to skip validation for (e.g., ['request', 'session'])

### Usage Modes

**Strict Mode (default)** - Raises exception:
```python
@validate_template("profile.html")
def render_profile():
    return {"username": "john"}  # Missing 'email' -> Exception
```

**Warn Mode** - Logs warning:
```python
@validate_template("profile.html", strict=False)
def render_profile():
    return {"username": "john"}  # Missing 'email' -> Warning logged
```

**With Ignore List**:
```python
@validate_template("profile.html", ignore=["request", "g", "session"])
def render_profile():
    return {"username": "john", "email": "john@example.com"}
```

### Error Messages

```python
class MissingTemplateVariable(Exception):
    """Raised when required template variable is missing."""
    pass

# Example error:
"""
MissingTemplateVariable: Template 'profile.html' requires variable 'email'

Template: templates/profile.html
Required variables: username, email, is_admin
Provided variables: request, username
Missing variables: email, is_admin

Variable 'email' is used at:
  - Line 15: {{ user.email }}
  - Line 42: <a href="mailto:{{ email }}">

Did you forget to pass this variable?
"""
```

## Implementation Details

### Core Logic

```python
import functools
from typing import Any, Callable, List, Optional
from pathlib import Path
from jinja2_validator import extract_variables

def validate_template(
    template_name: str,
    strict: bool = True,
    ignore: Optional[List[str]] = None,
    template_dir: Optional[Path] = None
) -> Callable:
    """
    Decorator to validate template context at runtime.

    Args:
        template_name: Name/path of template file
        strict: Raise exception on missing vars (True) or warn (False)
        ignore: List of variable names to ignore
        template_dir: Directory containing templates (auto-detect if None)

    Returns:
        Decorated function that validates context before execution

    Raises:
        MissingTemplateVariable: If strict=True and variables missing

    Example:
        @validate_template("profile.html")
        def render_profile():
            return {"username": "john", "email": "j@example.com"}
    """
    # Extract required variables from template
    if ignore is None:
        ignore = ["request", "g", "session"]

    template_path = _find_template(template_name, template_dir)
    required_vars = extract_variables(template_path)
    required_vars = set(required_vars) - set(ignore)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Call original function
            result = func(*args, **kwargs)

            # Extract context from result
            context = _extract_context(result)

            # Validate context
            missing_vars = required_vars - set(context.keys())

            if missing_vars:
                if strict:
                    raise MissingTemplateVariable(
                        f"Template '{template_name}' requires variables: {missing_vars}"
                    )
                else:
                    import warnings
                    warnings.warn(
                        f"Template '{template_name}' missing variables: {missing_vars}"
                    )

            return result

        return wrapper
    return decorator
```

### Context Extraction

Need to handle different return types:

```python
def _extract_context(result: Any) -> dict:
    """
    Extract context dictionary from function result.

    Handles:
    - dict: Direct context
    - TemplateResponse: FastAPI/Starlette
    - tuple: Flask (template, context)
    - Response: Django
    """
    # Plain dict
    if isinstance(result, dict):
        return result

    # FastAPI/Starlette TemplateResponse
    if hasattr(result, 'context'):
        return result.context

    # Flask tuple (template_name, context)
    if isinstance(result, tuple) and len(result) == 2:
        return result[1]

    # Django HttpResponse
    if hasattr(result, 'context_data'):
        return result.context_data

    return {}
```

### Template Discovery

```python
def _find_template(name: str, template_dir: Optional[Path]) -> Path:
    """
    Find template file.

    Search order:
    1. Provided template_dir
    2. ./templates
    3. Current directory
    """
    if template_dir:
        path = template_dir / name
        if path.exists():
            return path

    # Try common locations
    for base in [Path("templates"), Path(".")]:
        path = base / name
        if path.exists():
            return path

    raise FileNotFoundError(f"Template not found: {name}")
```

## Configuration

Support configuration file:

```toml
# .jinja2-validator.toml
[runtime]
strict = true
ignore_variables = ["request", "g", "session", "current_user"]
template_dir = "templates"

[runtime.development]
strict = false  # Only warn in development

[runtime.production]
strict = true  # Always fail in production
```

Load config:
```python
import os

def load_config():
    env = os.getenv("ENVIRONMENT", "development")
    config = load_toml(".jinja2-validator.toml")
    return config["runtime"].get(env, config["runtime"])
```

## Testing Strategy

### Unit Tests

```python
def test_decorator_catches_missing_variable():
    @validate_template("test.html")
    def render():
        return {"username": "john"}  # Missing 'email'

    with pytest.raises(MissingTemplateVariable):
        render()

def test_decorator_allows_complete_context():
    @validate_template("test.html")
    def render():
        return {"username": "john", "email": "j@example.com"}

    result = render()  # Should not raise
    assert result["username"] == "john"

def test_decorator_warn_mode():
    @validate_template("test.html", strict=False)
    def render():
        return {"username": "john"}  # Missing 'email'

    with pytest.warns(UserWarning):
        render()

def test_decorator_with_ignore_list():
    @validate_template("test.html", ignore=["email"])
    def render():
        return {"username": "john"}  # 'email' ignored

    render()  # Should not raise
```

### Integration Tests

Test with real frameworks:
- FastAPI integration test
- Flask integration test
- Plain Jinja2 integration test

## Performance Considerations

- **Cache template analysis**: Don't re-parse template on every request
- **Lazy loading**: Only parse template on first use
- **Disable in production**: Option to disable validation in prod (use env var)

```python
# Caching
_template_cache = {}

def extract_variables_cached(template_path: Path):
    if template_path not in _template_cache:
        _template_cache[template_path] = extract_variables(template_path)
    return _template_cache[template_path]
```

## Acceptance Criteria

- [ ] Decorator catches missing variables in strict mode
- [ ] Decorator warns about missing variables in warn mode
- [ ] Decorator ignores specified variables
- [ ] Works with plain dictionaries
- [ ] Works with FastAPI TemplateResponse
- [ ] Works with Flask tuples
- [ ] Clear error messages with helpful context
- [ ] Performance: <1ms overhead per request
- [ ] Configuration file support
- [ ] Environment-based configuration (dev/prod)
- [ ] Comprehensive test coverage
- [ ] Documentation with examples

## Related Issues

- #8 (FastAPI Integration)
- #9 (Flask Integration)
- #10 (Configuration System)

## Future Enhancements

- [ ] Type checking (validate variable types match expected)
- [ ] Async decorator support
- [ ] Middleware integration (auto-apply to all routes)
- [ ] Custom validation rules
- [ ] Variable value validation (not just presence)
