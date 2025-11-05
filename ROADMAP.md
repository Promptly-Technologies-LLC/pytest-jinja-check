# Jinja2 Validator - Project Roadmap

## Vision

Create a modern, actively maintained library for Jinja2 template analysis and runtime validation that fills the gap left by abandoned tools like jinja2schema.

## Core Value Proposition

- **Static Analysis**: Extract and document template variables
- **Runtime Validation**: Catch missing/incorrect context variables before rendering
- **Framework Integration**: First-class support for FastAPI, Flask, and Django
- **Developer Experience**: Clear error messages, easy setup, great docs

---

## Milestone 1: MVP (v0.1.0) - Foundation
**Goal**: Ship minimal viable package to PyPI with core functionality
**Timeline**: 2-3 weeks
**Target Users**: Early adopters, feedback seekers

### Features

#### Core Library
- [x] Variable extraction from templates (already implemented)
- [ ] Proper package structure with `src/` layout
- [ ] Configuration file support (`.jinja2-validator.toml`)
- [ ] Template syntax validation
- [ ] Comprehensive test suite (pytest)
- [ ] Type hints throughout codebase

#### CLI Tool
- [ ] `jinja2-validator check <directory>` - Validate all templates
- [ ] `jinja2-validator docs <directory>` - Generate documentation
- [ ] `jinja2-validator list-vars <template>` - Show variables for single template
- [ ] JSON output option for CI/CD integration
- [ ] Exit codes for CI/CD (0 = pass, 1 = fail)

#### Documentation
- [ ] Clean up README with accurate information
- [ ] Installation instructions
- [ ] Quick start guide
- [ ] CLI reference
- [ ] API documentation (basic)
- [ ] Contributing guidelines
- [ ] Code of conduct

#### Distribution
- [ ] PyPI package published
- [ ] GitHub releases automated
- [ ] Versioning strategy (semantic versioning)
- [ ] License file (MIT or Apache 2.0)

---

## Milestone 2: Runtime Validation (v0.2.0) - Killer Feature
**Goal**: Add runtime context validation - the unique selling point
**Timeline**: 2-3 weeks after MVP
**Target Users**: FastAPI/Flask developers with template-heavy apps

### Features

#### Core Validation
- [ ] `@validate_template()` decorator for functions
- [ ] Context validation at render time
- [ ] Descriptive error messages with line numbers
- [ ] Optional strict mode (fail) vs. warn mode
- [ ] Support for partial context validation
- [ ] Ignore common framework variables (request, session, etc.)

#### Framework Integrations
- [ ] FastAPI integration with decorator
- [ ] Flask integration with decorator
- [ ] Jinja2 Environment wrapper
- [ ] Example projects for each framework

#### Developer Experience
- [ ] Helpful error messages: "Missing variable 'email' required by profile.html:23"
- [ ] Development mode warnings (don't fail in dev)
- [ ] Production mode strict enforcement
- [ ] Environment-based configuration

#### Documentation
- [ ] Runtime validation guide
- [ ] Framework-specific tutorials
- [ ] Error message reference
- [ ] Migration guide from jinja2schema

---

## Milestone 3: Advanced Analysis (v0.3.0) - Power Features
**Goal**: Add sophisticated static analysis capabilities
**Timeline**: 3-4 weeks
**Target Users**: Large teams, complex codebases

### Features

#### Static Analysis
- [ ] Detect hardcoded URLs (suggest `url_for()`)
- [ ] Find unused variables passed to templates
- [ ] Detect undefined filters
- [ ] Track variable usage (where each variable is used)
- [ ] Template dependency graph (includes/extends)
- [ ] Circular dependency detection

#### Type Inference
- [ ] Infer variable types from usage patterns
- [ ] TypedDict/Pydantic model generation
- [ ] Type hint validation (if types provided)
- [ ] JSON Schema export (jinja2schema compatibility)

#### Security Analysis
- [ ] Detect potentially unsafe operations
- [ ] Flag missing `|safe` or `|escape` filters
- [ ] Check for XSS vulnerabilities
- [ ] Warn about user input rendering

#### Documentation
- [ ] Advanced analysis guide
- [ ] Security best practices
- [ ] Type system documentation
- [ ] Case studies from real projects

---

## Milestone 4: Testing & CI/CD (v0.4.0) - Team Features
**Goal**: Make it easy for teams to adopt and enforce
**Timeline**: 2-3 weeks
**Target Users**: Engineering teams, DevOps

### Features

#### Testing Tools
- [ ] `generate_mock_context()` - Auto-generate test data
- [ ] `TemplateTestCase` base class for pytest
- [ ] Snapshot testing support
- [ ] Coverage reporting for templates
- [ ] Test generation from templates

#### CI/CD Integration
- [ ] Pre-commit hook package
- [ ] GitHub Actions workflow template
- [ ] GitLab CI template
- [ ] Jenkins pipeline example
- [ ] Docker image for CI environments

#### Reporting
- [ ] HTML report generation
- [ ] JUnit XML output for CI tools
- [ ] GitHub PR comments integration
- [ ] Diff reporting (show what changed)
- [ ] Badge generation (shields.io)

#### Documentation
- [ ] CI/CD integration guide
- [ ] Pre-commit hook setup
- [ ] Testing best practices
- [ ] Team adoption guide

---

## Milestone 5: Django Integration (v0.5.0) - Ecosystem Expansion
**Goal**: Full Django support to reach broader audience
**Timeline**: 2-3 weeks
**Target Users**: Django developers

### Features

#### Django-Specific
- [ ] Django template tag/filter support
- [ ] Django management command
- [ ] Django settings integration
- [ ] Django Rest Framework integration
- [ ] Django template discovery
- [ ] Django context processors support

#### Documentation
- [ ] Django-specific guide
- [ ] Migration from Django's built-in validation
- [ ] Django best practices
- [ ] Example Django project

---

## Milestone 6: Developer Tools (v0.6.0) - DX Enhancement
**Goal**: Make the development experience exceptional
**Timeline**: 4-6 weeks
**Target Users**: All developers

### Features

#### IDE Integration
- [ ] Language Server Protocol (LSP) implementation
- [ ] VS Code extension
- [ ] PyCharm plugin
- [ ] Real-time linting in editor
- [ ] Auto-completion for template variables
- [ ] Jump to template definition

#### Advanced CLI
- [ ] Interactive mode
- [ ] Watch mode (continuous validation)
- [ ] Fix command (auto-fix common issues)
- [ ] Init command (project setup wizard)
- [ ] Template search/grep tool

#### Web UI
- [ ] Local web dashboard
- [ ] Visual template dependency graph
- [ ] Interactive documentation browser
- [ ] Template playground/tester

---

## Milestone 7: Performance & Scale (v1.0.0) - Production Ready
**Goal**: Handle large codebases efficiently, ship v1.0
**Timeline**: 3-4 weeks
**Target Users**: Enterprise teams

### Features

#### Performance
- [ ] Parallel template processing
- [ ] Incremental analysis (only changed files)
- [ ] Caching layer for repeated analysis
- [ ] Memory optimization for large projects
- [ ] Performance benchmarks

#### Scalability
- [ ] Support for 10,000+ templates
- [ ] Multi-project workspace support
- [ ] Monorepo support
- [ ] Remote template sources
- [ ] Plugin architecture

#### Enterprise Features
- [ ] Custom rule engine
- [ ] Organization-wide configuration
- [ ] Audit logging
- [ ] SAML/SSO for web UI (if applicable)
- [ ] Export/import capabilities

#### Documentation
- [ ] Performance tuning guide
- [ ] Architecture documentation
- [ ] Plugin development guide
- [ ] Enterprise deployment guide
- [ ] v1.0 release announcement

---

## Future Ideas (Post-1.0)

### Community & Ecosystem
- [ ] Third-party plugin marketplace
- [ ] Community rule sharing
- [ ] Template library integration
- [ ] Cookiecutter integration
- [ ] Yeoman generator integration

### Advanced Features
- [ ] AI-powered variable description generation
- [ ] Template refactoring tools
- [ ] Migration tools between template engines
- [ ] Visual template builder
- [ ] Template performance profiler

### Integrations
- [ ] Ansible integration (huge Jinja2 user)
- [ ] SaltStack integration
- [ ] Cookiecutter integration
- [ ] Static site generator integrations
- [ ] CMS integrations (Wagtail, Django CMS, etc.)

---

## Success Metrics

### MVP Success (v0.1.0)
- [ ] 100+ PyPI downloads/month
- [ ] 50+ GitHub stars
- [ ] 5+ community issues/PRs
- [ ] Posted on r/Python, HN

### v0.2.0 Success
- [ ] 500+ PyPI downloads/month
- [ ] 200+ GitHub stars
- [ ] 3+ production users testimonials
- [ ] Featured in a Python newsletter

### v1.0.0 Success
- [ ] 2,000+ PyPI downloads/month
- [ ] 1,000+ GitHub stars
- [ ] 10+ enterprise users
- [ ] Conference talk accepted
- [ ] Listed in awesome-python

---

## Non-Goals

These are explicitly out of scope to maintain focus:

- [ ] Template rendering engine (use Jinja2 itself)
- [ ] Template formatting (use djlint)
- [ ] HTML accessibility linting (use curlylint)
- [ ] Template language conversion (maybe post-1.0)
- [ ] Visual template editor (maybe post-1.0)

---

## Resource Requirements

### MVP Phase
- **Time**: ~40 hours
- **Skills**: Python packaging, CLI development, Jinja2 internals
- **Tools**: pytest, click/typer, pyproject.toml

### Runtime Validation Phase
- **Time**: ~40 hours
- **Skills**: Decorators, FastAPI/Flask, error handling
- **Tools**: FastAPI, Flask, comprehensive test frameworks

### Long-term Maintenance
- **Time**: 5-10 hours/week
- **Activities**: Issue triage, PR reviews, releases, docs
- **Community**: Discord/Slack channel, GitHub Discussions

---

## Risk Management

### Technical Risks
- **Risk**: Jinja2 AST parsing complexity
  - **Mitigation**: Leverage existing `jinja2.meta` module, add tests

- **Risk**: Performance with large template bases
  - **Mitigation**: Profile early, implement caching, parallel processing

- **Risk**: Framework integration breaking changes
  - **Mitigation**: Pin versions, comprehensive integration tests

### Market Risks
- **Risk**: djlint adds context validation
  - **Mitigation**: Different focus, collaboration opportunity

- **Risk**: Low adoption
  - **Mitigation**: Strong documentation, marketing, real-world examples

### Maintenance Risks
- **Risk**: Maintainer burnout
  - **Mitigation**: Start small, find co-maintainers, clear scope

---

## Decision Log

### Package Name: TBD
**Options**: jinja2-validator, jinja2-typeguard, jinja2-strict, template-guardian
**Decision**: [To be decided based on PyPI availability and feedback]

### License: MIT
**Rationale**: Most permissive, encourages adoption

### Framework Priority: FastAPI → Flask → Django
**Rationale**: FastAPI is modern and growing, Flask is ubiquitous, Django has built-in tooling

### Python Support: 3.9+
**Rationale**: Modern type hints, no legacy baggage, matches FastAPI

---

## Questions to Resolve

1. Should we support Jinja2 extensions? (Yes, but phase 2+)
2. Should we have a config file or environment variables? (Both)
3. Should we validate at import time or runtime? (Runtime, with CLI for static)
4. Should we integrate with existing linters or be standalone? (Standalone, but composable)
5. Should we support custom validation rules? (Yes, but post-MVP)
