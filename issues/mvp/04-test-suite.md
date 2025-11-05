---
title: Set up comprehensive test suite
labels: mvp, testing
milestone: v0.1.0
priority: P1
---

## Description

Establish a robust testing infrastructure with pytest, including unit tests, integration tests, and test fixtures.

## Goals

- 80%+ code coverage
- Fast test execution (<5 seconds)
- Clear test organization
- Easy to add new tests
- CI/CD ready

## Test Structure

```
tests/
├── unit/
│   ├── test_analyzer.py
│   ├── test_validator.py
│   ├── test_generator.py
│   └── test_cli.py
├── integration/
│   ├── test_cli_integration.py
│   └── test_end_to_end.py
├── fixtures/
│   ├── templates/
│   │   ├── valid/
│   │   │   ├── simple.html
│   │   │   ├── with_variables.html
│   │   │   └── with_includes.html
│   │   └── invalid/
│   │       ├── syntax_error.html
│   │       ├── undefined_filter.html
│   │       └── unclosed_block.html
│   └── expected_outputs/
│       ├── simple_vars.json
│       └── simple_docs.md
├── conftest.py
└── test_utils.py
```

## Acceptance Criteria

- [ ] pytest configured in `pyproject.toml`
- [ ] Test coverage reporting configured
- [ ] All core functions have unit tests
- [ ] CLI commands have integration tests
- [ ] Test fixtures for common scenarios
- [ ] Tests pass in Python 3.9, 3.10, 3.11, 3.12
- [ ] Documentation on running tests in README
- [ ] Pre-commit hook for running tests (optional)

## Test Categories

### Unit Tests

**test_analyzer.py**
- `test_extract_variables_simple()` - Basic variable extraction
- `test_extract_variables_nested()` - Nested objects (user.name)
- `test_extract_variables_filters()` - Variables with filters
- `test_extract_variables_loops()` - Variables in loops
- `test_extract_variables_conditionals()` - Variables in if blocks
- `test_no_variables()` - Template with no variables

**test_validator.py**
- `test_validate_syntax_valid()` - Valid template passes
- `test_validate_syntax_error()` - Syntax error detected
- `test_validate_undefined_filter()` - Unknown filter caught
- `test_validate_unclosed_block()` - Unclosed block detected
- `test_custom_filters()` - Custom filters registered

**test_generator.py**
- `test_generate_markdown_docs()` - Markdown generation
- `test_generate_with_grouping()` - Templates grouped by directory
- `test_generate_empty_templates()` - Handle templates with no vars
- `test_generate_with_descriptions()` - Variable descriptions

**test_cli.py**
- `test_cli_help()` - Help text displays
- `test_cli_version()` - Version displays correctly
- `test_cli_invalid_command()` - Unknown command fails gracefully

### Integration Tests

**test_cli_integration.py**
- `test_check_command_valid_templates()` - Check command with valid dir
- `test_check_command_invalid_templates()` - Check command with errors
- `test_check_command_json_output()` - JSON format output
- `test_docs_command()` - Documentation generation
- `test_list_vars_command()` - Single template variable list
- `test_recursive_directory_scan()` - Recursive template discovery

**test_end_to_end.py**
- `test_full_workflow()` - Complete workflow from CLI to output
- `test_ci_integration()` - Simulate CI/CD usage

## pytest Configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--cov=src/jinja2_validator",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
]
```

## Fixtures

### conftest.py

```python
import pytest
from pathlib import Path

@pytest.fixture
def valid_template():
    return """
    <h1>{{ title }}</h1>
    <p>Welcome, {{ user.name }}!</p>
    """

@pytest.fixture
def invalid_template():
    return """
    <h1>{{ title }}</h1>
    {% if user %}
    <p>Never closed!</p>
    """

@pytest.fixture
def template_dir(tmp_path):
    """Create temporary directory with test templates."""
    templates = tmp_path / "templates"
    templates.mkdir()

    (templates / "valid.html").write_text("""
        <h1>{{ title }}</h1>
    """)

    (templates / "invalid.html").write_text("""
        {% if x %}
    """)

    return templates

@pytest.fixture
def cli_runner():
    """Click CLI test runner."""
    from click.testing import CliRunner
    return CliRunner()
```

## Test Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-xdist>=3.0.0",  # Parallel test execution
    "pytest-mock>=3.10.0",
    "coverage[toml]>=7.0.0",
]
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/unit/test_analyzer.py

# Run specific test
pytest tests/unit/test_analyzer.py::test_extract_variables_simple

# Run in parallel
pytest -n auto

# Generate HTML coverage report
pytest --cov --cov-report=html
open htmlcov/index.html
```

## CI/CD Integration

Tests should run on:
- GitHub Actions (Linux, macOS, Windows)
- Multiple Python versions (3.9, 3.10, 3.11, 3.12)
- On every PR and push to main

## Coverage Goals

- Overall: 80%+ coverage
- Core modules (analyzer, validator): 90%+ coverage
- CLI module: 70%+ coverage (UI code is tricky)

## Related Issues

- #1 (Package Structure)
- #2 (CLI Tool)
- #3 (Syntax Validation)

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Testing Click applications](https://click.palletsprojects.com/en/stable/testing/)
