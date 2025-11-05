---
title: Write comprehensive documentation
labels: mvp, documentation
milestone: v0.1.0
priority: P1
---

## Description

Create high-quality documentation that makes it easy for developers to get started and use the tool effectively.

## Documentation Structure

```
docs/
├── getting-started.md
├── cli-reference.md
├── api-reference.md
├── configuration.md
├── examples/
│   ├── basic-usage.md
│   ├── ci-integration.md
│   └── custom-filters.md
├── contributing.md
└── changelog.md

README.md
LICENSE
CODE_OF_CONDUCT.md
CONTRIBUTING.md
```

## README.md Requirements

### Sections

1. **Header**
   - Project name and tagline
   - Badges (build status, coverage, PyPI version, Python versions)
   - One-sentence description

2. **The Problem**
   - Brief explanation of the pain point
   - Why existing tools aren't enough

3. **The Solution**
   - What this tool does differently
   - Key features (bullet points)

4. **Quick Start**
   - Installation: `pip install jinja2-validator`
   - Basic usage example (3-5 lines)
   - Link to full documentation

5. **Features**
   - Variable extraction
   - Syntax validation
   - Documentation generation
   - CI/CD integration

6. **Usage Examples**
   - CLI examples
   - Short code examples
   - Link to examples directory

7. **Installation**
   - PyPI: `pip install jinja2-validator`
   - From source: `pip install -e .`
   - Development: `pip install -e ".[dev]"`

8. **Documentation**
   - Links to full docs
   - CLI reference
   - API reference

9. **Contributing**
   - How to contribute
   - Link to CONTRIBUTING.md
   - Code of conduct

10. **License**
    - License type
    - Link to LICENSE file

11. **Acknowledgments**
    - Inspired by jinja2schema
    - Thanks to contributors

### Example README Skeleton

```markdown
# jinja2-validator

**Static analysis and runtime validation for Jinja2 templates**

[![Tests](badge)](link) [![Coverage](badge)](link) [![PyPI](badge)](link)

Stop runtime template errors before they reach production. jinja2-validator analyzes your Jinja2 templates to find missing variables, syntax errors, and undefined filters—all before you render.

## Why?

You're building a FastAPI/Flask app with Jinja2 templates. You rename a variable in your view but forget to update the template. Your tests pass because they don't actually render the template. Then production breaks. 😱

**jinja2-validator prevents this.**

## Features

- 🔍 **Variable extraction** - See what context variables each template needs
- ✅ **Syntax validation** - Catch template syntax errors before runtime
- 📚 **Auto documentation** - Generate docs showing required variables
- 🚀 **CI/CD ready** - JSON output, exit codes, pre-commit hooks
- 🎯 **Framework integration** - Decorators for FastAPI/Flask (coming soon)

## Quick Start

```bash
pip install jinja2-validator

# Check all templates
jinja2-validator check ./templates

# Generate documentation
jinja2-validator docs ./templates -o template_docs.md
```

## Documentation

Full documentation at [link]

- [Getting Started](link)
- [CLI Reference](link)
- [Examples](link)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Inspired by [jinja2schema](https://github.com/aromanovich/jinja2schema) (unmaintained).
```

## Getting Started Guide

Should cover:
- Installation
- First command
- Understanding output
- Common use cases
- Next steps

## CLI Reference

Document all commands with:
- Command syntax
- All options/flags
- Examples
- Output format

## API Reference

Document public API:
- `extract_variables(template_path)`
- `validate_syntax(template_path)`
- `generate_documentation(template_dir, output)`
- Configuration classes

Use docstrings to auto-generate API docs (Sphinx or mkdocs).

## Examples Directory

### Basic Usage (`examples/basic-usage.md`)
- Extract variables from single template
- Validate template directory
- Generate documentation

### CI Integration (`examples/ci-integration.md`)
- GitHub Actions workflow
- GitLab CI configuration
- Pre-commit hook setup

### Custom Filters (`examples/custom-filters.md`)
- Register custom filters
- Configuration file
- Validation with custom filters

## Acceptance Criteria

- [ ] README is clear, concise, and compelling
- [ ] Installation instructions work on all platforms
- [ ] Quick start can be completed in <5 minutes
- [ ] CLI reference documents all commands
- [ ] API reference has docstrings for all public functions
- [ ] At least 3 examples in examples directory
- [ ] CONTRIBUTING.md explains how to contribute
- [ ] CODE_OF_CONDUCT.md in place
- [ ] LICENSE file present (MIT)
- [ ] All links work
- [ ] Screenshots or asciinema demos (optional but nice)

## Documentation Tools

### Option 1: Simple Markdown
- Just markdown files
- No build step
- Easy to maintain
- Works great for MVP

### Option 2: MkDocs
- Static site generator
- Material theme looks great
- Can add later

### Option 3: Sphinx
- Python standard
- Auto-generates API docs
- More complex setup

**Recommendation for MVP**: Simple markdown in `docs/` directory. Can add MkDocs later.

## Badges

Add badges to README:
```markdown
[![Tests](https://github.com/user/repo/actions/workflows/tests.yml/badge.svg)](link)
[![Coverage](https://codecov.io/gh/user/repo/branch/main/graph/badge.svg)](link)
[![PyPI](https://img.shields.io/pypi/v/jinja2-validator.svg)](link)
[![Python](https://img.shields.io/pypi/pyversions/jinja2-validator.svg)](link)
[![License](https://img.shields.io/github/license/user/repo.svg)](link)
```

## Style Guide

- Use active voice
- Short sentences
- Code examples for everything
- Show both success and error cases
- Include "why" not just "how"

## Testing Documentation

- [ ] Follow all installation instructions in a clean environment
- [ ] Run all example commands
- [ ] Verify all links work
- [ ] Check for typos (automated spell check)
- [ ] Have someone unfamiliar with the project try it

## Related Issues

- #1 (Package Structure)
- #2 (CLI Tool)

## Future Documentation

- Video tutorials
- Blog post announcing the tool
- Conference talk slides
- Integration guides for popular frameworks
