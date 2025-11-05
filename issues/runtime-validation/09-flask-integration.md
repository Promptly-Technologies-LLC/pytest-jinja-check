---
title: Flask integration with context validation
labels: enhancement, runtime-validation, flask
milestone: v0.2.0
priority: P1
---

## Description

Create Flask-specific integration for runtime template validation that works with Flask's `render_template` and `render_template_string`.

## User Story

**As a Flask developer**, I want template validation that integrates naturally with Flask's templating system.

## Goals

- Works with `render_template()` and `render_template_string()`
- Blueprint support
- Flask context (g, session, request) awareness
- Development/production mode awareness
- Template inheritance support

## API Design

### Option 1: Decorator

```python
from flask import Flask, render_template
from jinja2_validator.flask import validate_template

app = Flask(__name__)

@app.route("/profile")
@validate_template("profile.html")
def profile():
    return render_template("profile.html",
        username="john",
        email="john@example.com"
    )
```

### Option 2: Validated render_template

```python
from jinja2_validator.flask import render_validated_template

@app.route("/profile")
def profile():
    return render_validated_template("profile.html",
        username="john",
        email="john@example.com"
    )
```

### Option 3: Monkey-patch (Global)

```python
from jinja2_validator.flask import enable_validation

app = Flask(__name__)
enable_validation(app, strict=True)

# All render_template calls are now validated!
@app.route("/profile")
def profile():
    return render_template("profile.html",
        username="john",
        email="john@example.com"
    )
```

**Recommendation**: Implement Options 1 and 2. Option 3 is powerful but might be surprising to users.

## Implementation

### Decorator Approach

```python
from functools import wraps
from flask import current_app
from jinja2_validator import extract_variables

def validate_template(template_name: str, strict: bool = True, ignore: list = None):
    """
    Decorator to validate Flask template context.

    Args:
        template_name: Template to validate
        strict: Raise exception on missing vars
        ignore: Variables to ignore (beyond Flask defaults)

    Example:
        @app.route("/profile")
        @validate_template("profile.html")
        def profile():
            return render_template("profile.html", username="john")
    """
    if ignore is None:
        ignore = []

    # Flask's default context variables
    flask_defaults = ["g", "request", "session", "config", "url_for", "get_flashed_messages"]
    ignore_set = set(flask_defaults + ignore)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Call original function
            result = func(*args, **kwargs)

            # If result is from render_template, validate
            # (This requires intercepting render_template - see below)

            return result
        return wrapper
    return decorator
```

### Validated render_template

```python
from flask import render_template as flask_render_template
from flask import current_app
from typing import Any

def render_validated_template(
    template_name_or_list: str,
    strict: bool = True,
    ignore: list = None,
    **context
) -> str:
    """
    Flask render_template with validation.

    Args:
        template_name_or_list: Template name(s)
        strict: Raise on missing vars
        ignore: Variables to ignore
        **context: Template context

    Returns:
        Rendered HTML

    Raises:
        MissingTemplateVariable: If strict and variables missing

    Example:
        return render_validated_template("profile.html",
            username="john",
            email="john@example.com"
        )
    """
    if ignore is None:
        ignore = []

    # Flask defaults
    flask_defaults = ["g", "request", "session", "config", "url_for", "get_flashed_messages"]
    ignore_set = set(flask_defaults + ignore)

    # Get template path
    template_name = (
        template_name_or_list[0]
        if isinstance(template_name_or_list, list)
        else template_name_or_list
    )

    # Extract required variables
    template_path = _find_flask_template(template_name)
    required_vars = extract_variables(template_path)
    required_vars = set(required_vars) - ignore_set

    # Check provided context
    # Note: Flask adds context processors, so we need to account for those
    provided_vars = set(context.keys())

    # Add Flask context processor variables
    with current_app.test_request_context():
        context_processors = current_app.template_context_processors
        for processor in context_processors.get(None, []):
            provided_vars.update(processor().keys())

    # Check for missing
    missing_vars = required_vars - provided_vars

    if missing_vars:
        if strict:
            raise MissingTemplateVariable(
                template=template_name,
                missing=missing_vars,
                required=required_vars,
                provided=provided_vars
            )
        else:
            import warnings
            warnings.warn(f"Template '{template_name}' missing: {missing_vars}")

    # Render normally
    return flask_render_template(template_name_or_list, **context)
```

### Helper: Find Flask Template

```python
from pathlib import Path
from flask import current_app

def _find_flask_template(template_name: str) -> Path:
    """
    Find Flask template file.

    Flask uses Jinja2 loader which can have multiple search paths.
    """
    # Get Flask's Jinja2 environment
    env = current_app.jinja_env

    # Get template source
    source, filename, uptodate = env.get_loader().get_source(env, template_name)

    return Path(filename)
```

### Monkey-patch Approach (Optional)

```python
import flask
from typing import Callable

_original_render_template = flask.render_template

def enable_validation(app, strict: bool = True, ignore: list = None):
    """
    Enable automatic validation for all render_template calls.

    Args:
        app: Flask application
        strict: Raise on missing vars
        ignore: Variables to ignore

    Example:
        app = Flask(__name__)
        enable_validation(app, strict=True)

        # All render_template calls now validated!
    """
    def validated_render_template(template_name_or_list, **context):
        return render_validated_template(
            template_name_or_list,
            strict=strict,
            ignore=ignore,
            **context
        )

    # Replace Flask's render_template
    flask.render_template = validated_render_template

def disable_validation():
    """Restore original render_template."""
    flask.render_template = _original_render_template
```

## Flask Context Processors

Flask has context processors that add variables to all templates. We need to account for these:

```python
def get_flask_context_processor_vars(app) -> set:
    """
    Get variables added by Flask context processors.

    These are automatically available in templates.
    """
    vars = set()

    with app.test_request_context():
        for processor_list in app.template_context_processors.values():
            for processor in processor_list:
                vars.update(processor().keys())

    return vars
```

## Blueprint Support

```python
from flask import Blueprint

bp = Blueprint("profile", __name__)

@bp.route("/profile")
@validate_template("profile.html")
def profile():
    return render_validated_template("profile.html",
        username="john",
        email="john@example.com"
    )
```

Should work automatically with decorated approach.

## Configuration

### App Config

```python
app.config['TEMPLATE_VALIDATION_STRICT'] = True
app.config['TEMPLATE_VALIDATION_IGNORE'] = ['custom_var']

# Use in decorator
@app.route("/profile")
@validate_template("profile.html",
    strict=app.config.get('TEMPLATE_VALIDATION_STRICT', True),
    ignore=app.config.get('TEMPLATE_VALIDATION_IGNORE', [])
)
def profile():
    return render_template("profile.html", username="john")
```

### Environment-based

```python
import os

strict_mode = os.getenv("FLASK_ENV") != "development"

app.config['TEMPLATE_VALIDATION_STRICT'] = strict_mode
```

## Error Handling

### Custom Error Page

```python
from jinja2_validator import MissingTemplateVariable

@app.errorhandler(MissingTemplateVariable)
def handle_template_error(error):
    """Show helpful error page for template validation errors."""
    if app.debug:
        return f"""
        <html>
            <body>
                <h1>Template Validation Error</h1>
                <p><strong>Template:</strong> {error.template}</p>
                <p><strong>Missing:</strong> {', '.join(error.missing)}</p>
                <p><strong>Required:</strong> {', '.join(error.required)}</p>
                <p><strong>Provided:</strong> {', '.join(error.provided)}</p>
            </body>
        </html>
        """, 500
    else:
        return "Internal Server Error", 500
```

## Testing

### Unit Tests

```python
import pytest
from flask import Flask

def test_render_validated_template_success():
    """Test that valid context renders."""
    app = Flask(__name__)

    with app.test_request_context():
        html = render_validated_template("test.html",
            username="john",
            email="john@example.com"
        )
        assert "john" in html

def test_render_validated_template_missing_var():
    """Test that missing variable raises."""
    app = Flask(__name__)

    with app.test_request_context():
        with pytest.raises(MissingTemplateVariable):
            render_validated_template("test.html",
                username="john"
                # Missing 'email'
            )

def test_decorator_with_context_processor():
    """Test that context processors are considered."""
    app = Flask(__name__)

    @app.context_processor
    def inject_user():
        return {"current_user": "admin"}

    @app.route("/test")
    @validate_template("test.html")
    def test_route():
        # current_user provided by context processor
        return render_template("test.html")

    with app.test_client() as client:
        response = client.get("/test")
        assert response.status_code == 200
```

### Integration Tests

```python
def test_full_flask_app():
    """Test with complete Flask application."""
    app = Flask(__name__)

    @app.route("/profile")
    def profile():
        return render_validated_template("profile.html",
            username="john",
            email="john@example.com"
        )

    @app.route("/broken")
    def broken():
        return render_validated_template("profile.html",
            username="john"
            # Missing email - should fail!
        )

    client = app.test_client()

    # Good route works
    response = client.get("/profile")
    assert response.status_code == 200

    # Broken route fails
    with pytest.raises(MissingTemplateVariable):
        client.get("/broken")
```

## Documentation

### Quick Start

```markdown
## Flask Integration

### Installation

```bash
pip install jinja2-validator[flask]
```

### Usage

#### Option 1: Validated render function

```python
from jinja2_validator.flask import render_validated_template

@app.route("/profile")
def profile():
    return render_validated_template("profile.html",
        username="john",
        email="john@example.com"
    )
```

#### Option 2: Decorator

```python
from jinja2_validator.flask import validate_template

@app.route("/profile")
@validate_template("profile.html")
def profile():
    return render_template("profile.html",
        username="john",
        email="john@example.com"
    )
```

### Configuration

```python
app.config['TEMPLATE_VALIDATION_STRICT'] = True
app.config['TEMPLATE_VALIDATION_IGNORE'] = ['my_custom_var']
```
```

## Acceptance Criteria

- [ ] `validate_template` decorator works with Flask routes
- [ ] `render_validated_template` function works
- [ ] Flask context variables (g, session, request) ignored by default
- [ ] Context processors accounted for
- [ ] Blueprint support
- [ ] Configuration via app.config
- [ ] Custom error handler for template errors
- [ ] Development vs production mode support
- [ ] Comprehensive tests with Flask test client
- [ ] Example Flask app
- [ ] Documentation with usage examples

## Related Issues

- #7 (Runtime Decorator)
- #8 (FastAPI Integration)
- #10 (Configuration System)

## Future Enhancements

- [ ] Flask-Admin integration
- [ ] Flask-Login integration (ignore current_user)
- [ ] Flask-WTF form integration
- [ ] Before/after request hooks for validation
