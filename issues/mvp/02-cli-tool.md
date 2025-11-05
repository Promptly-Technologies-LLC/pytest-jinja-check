---
title: Implement CLI tool with basic commands
labels: mvp, feature, cli
milestone: v0.1.0
priority: P0
---

## Description

Create a command-line interface with three core commands: `check`, `docs`, and `list-vars`.

## User Stories

**As a developer**, I want to:
- Run `jinja2-validator check ./templates` to validate all templates
- Run `jinja2-validator docs ./templates` to generate documentation
- Run `jinja2-validator list-vars template.html` to see variables for one template
- Get JSON output for CI/CD integration
- See helpful error messages with line numbers

## Commands Specification

### `jinja2-validator check <directory>`

Validate all templates in a directory.

**Options:**
- `--recursive` / `-r`: Search subdirectories (default: true)
- `--format`: Output format (`text`, `json`) (default: text)
- `--fail-on-error`: Exit with code 1 on any error (default: true)
- `--ignore-vars`: Variables to ignore (e.g., `request,session`)

**Output (text):**
```
Checking templates in ./templates...
✓ templates/base.html (3 variables)
✓ templates/profile.html (5 variables)
✗ templates/dashboard.html: Syntax error at line 23
  Unexpected token: %}

Summary: 2 valid, 1 error
```

**Output (json):**
```json
{
  "summary": {
    "total": 3,
    "valid": 2,
    "errors": 1
  },
  "templates": [
    {
      "path": "templates/base.html",
      "valid": true,
      "variables": ["title", "user", "messages"]
    },
    {
      "path": "templates/dashboard.html",
      "valid": false,
      "error": "Syntax error at line 23: Unexpected token: %}"
    }
  ]
}
```

### `jinja2-validator docs <directory>`

Generate markdown documentation for all templates.

**Options:**
- `--output` / `-o`: Output file (default: `template_variables.md`)
- `--format`: Output format (`markdown`, `html`, `json`) (default: markdown)
- `--recursive` / `-r`: Search subdirectories (default: true)
- `--ignore-vars`: Variables to ignore from output

**Output:**
Creates a markdown file documenting all template variables (existing functionality).

### `jinja2-validator list-vars <template>`

Show variables for a single template.

**Options:**
- `--format`: Output format (`text`, `json`) (default: text)
- `--show-line-numbers`: Show where each variable is used

**Output (text):**
```
Variables in templates/profile.html:
- username (line 12, 24)
- email (line 15)
- is_admin (line 30)
- avatar_url (line 8)
```

**Output (json):**
```json
{
  "template": "templates/profile.html",
  "variables": [
    {
      "name": "username",
      "lines": [12, 24]
    },
    {
      "name": "email",
      "lines": [15]
    }
  ]
}
```

## Acceptance Criteria

- [ ] All three commands work as specified
- [ ] Exit codes: 0 for success, 1 for errors
- [ ] JSON output is valid and parsable
- [ ] Error messages include file paths and line numbers
- [ ] Help text is clear and comprehensive (`--help`)
- [ ] Progress indicators for long operations (optional for MVP)
- [ ] CLI works on Windows, macOS, and Linux

## Implementation Notes

### CLI Framework
Recommend **Click** for:
- Simple decorator-based API
- Great help text generation
- Built-in parameter validation
- Color support

Alternative: **Typer** (Click-based with type hints)

### Directory Walking
Use `pathlib.Path.rglob()` for recursive template discovery.

### Line Number Tracking
Need to enhance `extract_template_variables()` to return line numbers. Use Jinja2 AST node locations.

### Configuration File Support
Future enhancement: Load options from `.jinja2-validator.toml` or `pyproject.toml`.

## Testing Strategy

- Unit tests for each command
- Integration tests with sample template directories
- Test error conditions (invalid templates, missing files)
- Test both text and JSON output formats
- Test CLI help output

## Dependencies

- `click>=8.0.0` or `typer>=0.9.0`
- `rich` (optional, for pretty output)
- `pathlib` (stdlib)

## Related Issues

- #1 (Package Structure)
- #4 (Syntax Validation)
- #5 (Documentation Generation)

## Example Usage

```bash
# Check all templates
jinja2-validator check ./templates

# Generate docs
jinja2-validator docs ./templates -o docs/templates.md

# Check single template
jinja2-validator list-vars templates/profile.html

# CI/CD integration
jinja2-validator check ./templates --format json | jq '.summary.errors'
```
