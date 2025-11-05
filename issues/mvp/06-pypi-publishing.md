---
title: Set up PyPI publishing workflow
labels: mvp, infrastructure, deployment
milestone: v0.1.0
priority: P2
---

## Description

Configure automated publishing to PyPI with proper versioning, releases, and changelog management.

## Goals

- Publish package to PyPI
- Automated releases via GitHub Actions
- Semantic versioning
- Automated changelog generation
- TestPyPI for testing releases

## Pre-Publishing Checklist

- [ ] Package name available on PyPI
- [ ] Package name matches project (no typos!)
- [ ] License file present (MIT recommended)
- [ ] README.md is comprehensive
- [ ] Version number in `__version__.py`
- [ ] All tests passing
- [ ] Code coverage >80%

## Package Metadata

Ensure `pyproject.toml` has complete metadata:

```toml
[project]
name = "jinja2-validator"
version = "0.1.0"
description = "Static analysis and runtime validation for Jinja2 templates"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = ["jinja2", "templates", "validation", "linting", "static-analysis"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Quality Assurance",
    "Topic :: Software Development :: Testing",
    "Topic :: Text Processing :: Markup :: HTML",
]

[project.urls]
Homepage = "https://github.com/username/jinja2-validator"
Documentation = "https://github.com/username/jinja2-validator#readme"
Repository = "https://github.com/username/jinja2-validator"
Issues = "https://github.com/username/jinja2-validator/issues"
Changelog = "https://github.com/username/jinja2-validator/blob/main/CHANGELOG.md"
```

## Version Management

### Using __version__.py

```python
# src/jinja2_validator/__version__.py
__version__ = "0.1.0"
```

### Single Source of Truth

Use `hatch-vcs` or similar to sync version from git tags:

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[tool.hatch.version]
source = "vcs"

[tool.hatch.build.hooks.vcs]
version-file = "src/jinja2_validator/__version__.py"
```

## PyPI Account Setup

1. Create account on [PyPI](https://pypi.org/)
2. Create account on [TestPyPI](https://test.pypi.org/)
3. Enable 2FA
4. Generate API tokens:
   - PyPI: Account → API tokens → Add API token (scope: entire account or specific project)
   - TestPyPI: Same process

## GitHub Secrets

Add secrets to GitHub repository:
- `PYPI_API_TOKEN` - PyPI API token
- `TEST_PYPI_API_TOKEN` - TestPyPI API token

Settings → Secrets and variables → Actions → New repository secret

## GitHub Actions Workflow

### Test Release to TestPyPI

`.github/workflows/test-release.yml`:

```yaml
name: Test Release

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install build dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Check package
        run: twine check dist/*

      - name: Publish to TestPyPI
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.TEST_PYPI_API_TOKEN }}
        run: |
          twine upload --repository testpypi dist/*
```

### Production Release

`.github/workflows/release.yml`:

```yaml
name: Release

on:
  release:
    types: [published]

jobs:
  build-and-publish:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: |
          twine upload dist/*
```

## Release Process

### Manual Release Steps

1. Update version in appropriate place
2. Update CHANGELOG.md
3. Commit changes: `git commit -m "Release v0.1.0"`
4. Create git tag: `git tag -a v0.1.0 -m "Release v0.1.0"`
5. Push commits and tags: `git push && git push --tags`
6. Create GitHub release from tag
7. GitHub Actions will automatically publish to PyPI

### Automated Release

Use [Release Drafter](https://github.com/release-drafter/release-drafter) or [semantic-release](https://github.com/semantic-release/semantic-release) for automatic releases.

## Changelog Management

### Format

Use [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New feature X

### Changed
- Modified behavior Y

### Fixed
- Bug fix Z

## [0.1.0] - 2025-01-15

### Added
- Initial release
- Variable extraction from templates
- Syntax validation
- CLI tool with check, docs, and list-vars commands
- Documentation generation

[Unreleased]: https://github.com/user/repo/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/user/repo/releases/tag/v0.1.0
```

## Testing the Release

### Test Installation from TestPyPI

```bash
# Create clean virtual environment
python -m venv test-env
source test-env/bin/activate  # or test-env\Scripts\activate on Windows

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ jinja2-validator

# Test the package
jinja2-validator --version
jinja2-validator --help
```

### Test Installation from PyPI

```bash
# After publishing to PyPI
pip install jinja2-validator
jinja2-validator --version
```

## Acceptance Criteria

- [ ] Package successfully builds with `python -m build`
- [ ] Package passes `twine check dist/*`
- [ ] Successfully published to TestPyPI
- [ ] Successfully installed from TestPyPI
- [ ] CLI works after installation from TestPyPI
- [ ] GitHub Actions workflow configured
- [ ] GitHub secrets configured
- [ ] CHANGELOG.md created
- [ ] Successfully published to PyPI
- [ ] Package appears on https://pypi.org/project/jinja2-validator/
- [ ] README renders correctly on PyPI

## Common Issues

### Issue: Package name already taken
**Solution**: Choose a different name, check variations

### Issue: README doesn't render on PyPI
**Solution**: Ensure `readme = "README.md"` in pyproject.toml and file exists

### Issue: Build fails
**Solution**: Check pyproject.toml syntax, ensure all files included

### Issue: Upload fails with 403
**Solution**: Check API token is correct and has right scope

## Security Best Practices

- Never commit API tokens to git
- Use GitHub Secrets for sensitive data
- Enable 2FA on PyPI account
- Use project-scoped tokens when possible
- Rotate tokens periodically

## Monitoring

After publishing:
- Monitor PyPI download stats
- Watch for issues filed on GitHub
- Check for security vulnerabilities (Dependabot)
- Monitor PyPI project page for feedback

## Related Issues

- #1 (Package Structure)
- #5 (Documentation)

## References

- [PyPA Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine documentation](https://twine.readthedocs.io/)
- [GitHub Actions for Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
