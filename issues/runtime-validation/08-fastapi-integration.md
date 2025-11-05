---
title: FastAPI integration with context validation
labels: enhancement, runtime-validation, fastapi
milestone: v0.2.0
priority: P0
---

## Description

Create FastAPI-specific integration for runtime template validation that works seamlessly with FastAPI's `TemplateResponse`.

## User Story

**As a FastAPI developer**, I want template validation that understands FastAPI's patterns and integrates naturally with my existing code.

## Goals

- Zero-friction FastAPI integration
- Works with `Jinja2Templates` and `TemplateResponse`
- Dependency injection compatible
- Async support
- Type-hint friendly

## API Design

### Option 1: Decorator (Simple)

```python
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from jinja2_validator.fastapi import validate_template

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/profile")
@validate_template("profile.html")
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": "john",
        "email": "john@example.com"
    })
```

### Option 2: Validated Template Response (Explicit)

```python
from jinja2_validator.fastapi import ValidatedTemplateResponse

@app.get("/profile")
async def profile(request: Request):
    return ValidatedTemplateResponse(
        templates,
        "profile.html",
        {
            "request": request,
            "username": "john",
            "email": "john@example.com"
        }
    )
```

### Option 3: Custom Jinja2Templates Class (Drop-in Replacement)

```python
from jinja2_validator.fastapi import ValidatedJinja2Templates

# Drop-in replacement for Jinja2Templates
templates = ValidatedJinja2Templates(directory="templates", strict=True)

@app.get("/profile")
async def profile(request: Request):
    # Automatically validated!
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": "john",
        "email": "john@example.com"
    })
```

**Recommendation**: Implement all three options. Option 3 is easiest for users, Option 1 is most explicit.

## Implementation

### ValidatedJinja2Templates

```python
from fastapi.templating import Jinja2Templates
from fastapi import Request
from typing import Any, Dict, Optional
from jinja2_validator import extract_variables

class ValidatedJinja2Templates(Jinja2Templates):
    """
    Drop-in replacement for FastAPI's Jinja2Templates with validation.

    Args:
        directory: Template directory
        strict: Raise exception on missing vars (default: True)
        ignore: Variables to ignore (default: ["request"])
        cache: Cache template analysis (default: True)

    Example:
        templates = ValidatedJinja2Templates(directory="templates")

        @app.get("/profile")
        async def profile(request: Request):
            return templates.TemplateResponse("profile.html", {
                "request": request,
                "username": "john"
            })
    """

    def __init__(
        self,
        directory: str,
        strict: bool = True,
        ignore: Optional[list] = None,
        cache: bool = True,
        **kwargs
    ):
        super().__init__(directory=directory, **kwargs)
        self.strict = strict
        self.ignore = ignore or ["request"]
        self.cache = cache
        self._variable_cache = {}

    def TemplateResponse(
        self,
        name: str,
        context: Dict[str, Any],
        **kwargs
    ):
        """
        Render template with validation.

        Validates context before rendering.
        """
        # Validate context
        self._validate_context(name, context)

        # Call parent method
        return super().TemplateResponse(name, context, **kwargs)

    def _validate_context(self, template_name: str, context: Dict[str, Any]):
        """Validate that context has all required variables."""
        # Get required variables (cached)
        required_vars = self._get_required_variables(template_name)

        # Check for missing variables
        provided_vars = set(context.keys())
        missing_vars = required_vars - provided_vars

        if missing_vars:
            if self.strict:
                raise MissingTemplateVariable(
                    template=template_name,
                    missing=missing_vars,
                    required=required_vars,
                    provided=provided_vars
                )
            else:
                import warnings
                warnings.warn(
                    f"Template '{template_name}' missing variables: {missing_vars}"
                )

    def _get_required_variables(self, template_name: str) -> set:
        """Get required variables for template (with caching)."""
        if not self.cache or template_name not in self._variable_cache:
            template_path = self.env.get_template(template_name).filename
            variables = extract_variables(template_path)
            variables = set(variables) - set(self.ignore)

            if self.cache:
                self._variable_cache[template_name] = variables
            return variables

        return self._variable_cache[template_name]
```

### ValidatedTemplateResponse

```python
from fastapi.responses import HTMLResponse
from starlette.background import BackgroundTask
from typing import Any, Dict, Optional

class ValidatedTemplateResponse(HTMLResponse):
    """
    TemplateResponse with automatic validation.

    Args:
        templates: Jinja2Templates instance
        name: Template name
        context: Template context
        strict: Raise on missing vars (default: True)
        ignore: Variables to ignore

    Example:
        return ValidatedTemplateResponse(
            templates,
            "profile.html",
            {"username": "john"}
        )
    """

    def __init__(
        self,
        templates: Jinja2Templates,
        name: str,
        context: Dict[str, Any],
        strict: bool = True,
        ignore: Optional[list] = None,
        status_code: int = 200,
        headers: Optional[dict] = None,
        background: Optional[BackgroundTask] = None,
    ):
        # Validate context
        _validate_template_context(name, context, templates, strict, ignore)

        # Render template
        content = templates.get_template(name).render(context)

        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            background=background
        )
```

### Decorator

```python
from functools import wraps
from typing import Callable

def validate_template(template_name: str, **validation_kwargs):
    """
    Decorator for FastAPI route handlers.

    Args:
        template_name: Template to validate against
        **validation_kwargs: Passed to validation (strict, ignore, etc.)

    Example:
        @app.get("/profile")
        @validate_template("profile.html")
        async def profile(request: Request):
            return templates.TemplateResponse(...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Call original function
            response = await func(*args, **kwargs)

            # Extract context from TemplateResponse
            if hasattr(response, 'context'):
                context = response.context
                _validate_template_context(
                    template_name,
                    context,
                    **validation_kwargs
                )

            return response

        return wrapper
    return decorator
```

## Exception Handling

### Custom Exception

```python
from fastapi import HTTPException

class MissingTemplateVariable(HTTPException):
    """
    Raised when template is missing required variables.

    In development: Shows detailed error page
    In production: Returns 500 error (customizable)
    """

    def __init__(
        self,
        template: str,
        missing: set,
        required: set,
        provided: set,
        status_code: int = 500
    ):
        self.template = template
        self.missing = missing
        self.required = required
        self.provided = provided

        detail = self._format_error()
        super().__init__(status_code=status_code, detail=detail)

    def _format_error(self) -> str:
        return f"""
Template Validation Error

Template: {self.template}
Missing variables: {', '.join(self.missing)}

Required: {', '.join(self.required)}
Provided: {', '.join(self.provided)}
        """.strip()
```

### Error Handler

```python
from fastapi import Request
from fastapi.responses import HTMLResponse

@app.exception_handler(MissingTemplateVariable)
async def template_error_handler(request: Request, exc: MissingTemplateVariable):
    """
    Custom error page for template validation errors.

    Shows helpful debug information in development.
    """
    if app.debug:
        # Show detailed error in development
        return HTMLResponse(
            content=f"""
            <html>
                <body style="font-family: monospace; padding: 20px;">
                    <h1>Template Validation Error</h1>
                    <p><strong>Template:</strong> {exc.template}</p>
                    <p><strong>Missing variables:</strong> {', '.join(exc.missing)}</p>

                    <h2>Details</h2>
                    <p><strong>Required:</strong> {', '.join(exc.required)}</p>
                    <p><strong>Provided:</strong> {', '.join(exc.provided)}</p>

                    <h2>How to fix</h2>
                    <p>Add the missing variables to your template context:</p>
                    <pre>{{
    "request": request,
    {', '.join(f'"{v}": ...' for v in exc.missing)}
}}</pre>
                </body>
            </html>
            """,
            status_code=500
        )
    else:
        # Production: Simple error
        return HTMLResponse(
            content="<h1>Internal Server Error</h1>",
            status_code=500
        )
```

## Configuration

### Environment-based

```python
import os

# Development: Warn only
if os.getenv("ENVIRONMENT") == "development":
    templates = ValidatedJinja2Templates(
        directory="templates",
        strict=False  # Warn but don't fail
    )

# Production: Strict
else:
    templates = ValidatedJinja2Templates(
        directory="templates",
        strict=True  # Fail on missing vars
    )
```

### Settings Integration

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    template_validation_strict: bool = True
    template_validation_ignore: list = ["request", "current_user"]

settings = Settings()

templates = ValidatedJinja2Templates(
    directory="templates",
    strict=settings.template_validation_strict,
    ignore=settings.template_validation_ignore
)
```

## Testing

### Unit Tests

```python
import pytest
from fastapi.testclient import TestClient

def test_validated_templates_success(app, client):
    """Test that valid context passes."""
    response = client.get("/profile")
    assert response.status_code == 200

def test_validated_templates_missing_var(app, client):
    """Test that missing variable raises error."""
    with pytest.raises(MissingTemplateVariable):
        client.get("/broken-profile")

def test_validated_templates_warn_mode(app, client):
    """Test that warn mode doesn't raise."""
    # Configure with strict=False
    templates = ValidatedJinja2Templates(directory="templates", strict=False)

    with pytest.warns(UserWarning):
        response = client.get("/profile")
        assert response.status_code == 200
```

### Integration Tests

Create example FastAPI app in `tests/`:

```python
# tests/fastapi_example.py
from fastapi import FastAPI, Request
from jinja2_validator.fastapi import ValidatedJinja2Templates

app = FastAPI()
templates = ValidatedJinja2Templates(directory="tests/fixtures/templates")

@app.get("/good")
async def good(request: Request):
    return templates.TemplateResponse("test.html", {
        "request": request,
        "username": "john",
        "email": "john@example.com"
    })

@app.get("/bad")
async def bad(request: Request):
    return templates.TemplateResponse("test.html", {
        "request": request,
        "username": "john"
        # Missing 'email'!
    })
```

## Documentation

### Quick Start

```markdown
## FastAPI Integration

### Installation

```bash
pip install jinja2-validator[fastapi]
```

### Usage

Replace `Jinja2Templates` with `ValidatedJinja2Templates`:

```python
from jinja2_validator.fastapi import ValidatedJinja2Templates

templates = ValidatedJinja2Templates(directory="templates")
```

That's it! Your templates are now validated automatically.

### Configuration

```python
templates = ValidatedJinja2Templates(
    directory="templates",
    strict=True,  # Raise exceptions (default)
    ignore=["request", "current_user"],  # Variables to ignore
    cache=True  # Cache template analysis (default)
)
```
```

## Acceptance Criteria

- [ ] `ValidatedJinja2Templates` class implemented
- [ ] Works as drop-in replacement for `Jinja2Templates`
- [ ] `ValidatedTemplateResponse` class implemented
- [ ] `@validate_template` decorator implemented
- [ ] All three APIs work correctly
- [ ] Async route handler support
- [ ] Custom exception with helpful messages
- [ ] Exception handler for development
- [ ] Configuration via settings
- [ ] Comprehensive tests with TestClient
- [ ] Example FastAPI app
- [ ] Documentation with usage examples
- [ ] Type hints throughout

## Related Issues

- #7 (Runtime Decorator)
- #9 (Flask Integration)
- #10 (Configuration System)

## Future Enhancements

- [ ] Dependency injection for template validation
- [ ] Middleware for automatic validation
- [ ] Integration with FastAPI's OpenAPI docs
- [ ] Type checking with Pydantic models
