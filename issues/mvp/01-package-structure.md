---
title: Set up proper Python package structure
labels: mvp, infrastructure
milestone: v0.1.0
priority: P0
---

## Description

Restructure the project into a proper Python package with modern packaging standards using `src/` layout.

## Current State

- Single script `generate_template_docs.py` in root
- No proper package structure
- Missing `pyproject.toml`
- Not installable via pip

## Goals

- [x] Adopt `src/` layout for better package isolation
- [x] Create proper `pyproject.toml` with all metadata
- [x] Set up entry points for CLI commands
- [x] Make package pip installable locally
- [x] Set up development dependencies

## Acceptance Criteria

- [ ] Package can be installed with `pip install -e .`
- [ ] Package has proper structure:
  ```
  src/jinja2_validator/
  ├── __init__.py
  ├── __version__.py
  ├── analyzer.py
  ├── cli.py
  └── generator.py
  ```
- [ ] `pyproject.toml` includes:
  - Project metadata (name, version, description, authors)
  - Dependencies (jinja2, click/typer)
  - Dev dependencies (pytest, black, mypy, ruff)
  - Entry points for CLI
  - Build backend (hatchling or setuptools)
- [ ] CLI command `jinja2-validator` is available after install
- [ ] README has installation instructions

## Implementation Notes

### Package Name Decision
Need to check PyPI availability:
- `jinja2-validator`
- `jinja2-typeguard`
- `jinja2-strict`
- `template-guardian`

### Suggested pyproject.toml structure
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "jinja2-validator"  # TBD
version = "0.1.0"
description = "Static analysis and runtime validation for Jinja2 templates"
authors = [{name = "Your Name", email = "your.email@example.com"}]
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
dependencies = [
    "jinja2>=3.0.0",
    "click>=8.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov",
    "black",
    "ruff",
    "mypy",
]

[project.scripts]
jinja2-validator = "jinja2_validator.cli:main"
```

## Testing Strategy

- Test package can be installed in clean virtual environment
- Test CLI entry point works
- Test imports work correctly

## Related Issues

- #2 (CLI Tool Implementation)
- #3 (Test Suite Setup)

## References

- [PyPA Packaging Guide](https://packaging.python.org/)
- [src layout explanation](https://hynek.me/articles/testing-packaging/)
