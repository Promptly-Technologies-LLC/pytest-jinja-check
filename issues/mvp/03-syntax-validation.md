---
title: Add template syntax validation
labels: mvp, feature
milestone: v0.1.0
priority: P0
---

## Description

Validate that all templates have valid Jinja2 syntax and provide clear error messages with line numbers when syntax errors are found.

## Current State

- Variable extraction works
- No explicit syntax checking
- Users only see errors when rendering templates

## Goals

- Parse all templates to check syntax
- Report syntax errors with line numbers
- Check for undefined filters
- Check for undefined tests
- Validate macro/block structure

## Acceptance Criteria

- [ ] Detect syntax errors (invalid Jinja2 syntax)
- [ ] Detect undefined filters (e.g., `{{ value|nonexistent }}`)
- [ ] Detect undefined tests (e.g., `{% if value is nonexistent %}`)
- [ ] Provide error messages with:
  - File path
  - Line number
  - Column number (if available)
  - Error description
  - Code snippet showing the error
- [ ] Validate macro calls (correct number of arguments)
- [ ] Check for unclosed blocks/tags

## Error Message Examples

### Good Error Message
```
Error in templates/profile.html:

  Line 23, Column 15:
    {{ user.name|nonexistent }}
                 ^^^^^^^^^^
    Unknown filter: nonexistent

  Suggestion: Did you mean 'capitalize'?
```

### Another Example
```
Error in templates/dashboard.html:

  Line 45:
    {% if user.is_admin %}
    ...
    (end of file)

    Unclosed block 'if' starting at line 45
```

## Implementation Notes

### Syntax Checking

Use Jinja2's built-in parser:

```python
from jinja2 import Environment, TemplateSyntaxError

def validate_syntax(template_path: Path) -> ValidationResult:
    env = Environment()
    try:
        with open(template_path) as f:
            env.parse(f.read())
        return ValidationResult(valid=True)
    except TemplateSyntaxError as e:
        return ValidationResult(
            valid=False,
            error=str(e),
            line=e.lineno,
            file=str(template_path)
        )
```

### Filter/Test Validation

Create a custom Environment with known filters/tests:

```python
env = Environment()
# Standard filters are already registered
# Can add custom filters if needed
env.filters['custom_filter'] = lambda x: x

# Check if filter exists
ast = env.parse(template_source)
# Walk AST looking for Filter nodes
# Check if filter.name in env.filters
```

### Configuration for Custom Filters

Users should be able to register custom filters:

```toml
# .jinja2-validator.toml
[filters]
myfilter = true
another_filter = true

[tests]
mytest = true
```

Or via CLI:
```bash
jinja2-validator check ./templates --filter myfilter --filter another_filter
```

### AST Walking

Need to walk the Jinja2 AST to find:
- Filter nodes → check filter name
- Test nodes → check test name
- Call nodes → check macro signatures
- Block nodes → ensure they're closed

```python
from jinja2 import nodes

class TemplateValidator(nodes.NodeTransformer):
    def visit_Filter(self, node):
        if node.name not in self.env.filters:
            self.errors.append(f"Undefined filter: {node.name}")
        return node
```

## Testing Strategy

### Test Cases

1. **Valid Templates**
   - Should pass validation
   - No errors reported

2. **Syntax Errors**
   - Missing closing tags: `{% if x %}`
   - Invalid syntax: `{{ if x }}`
   - Malformed expressions: `{{ user. }}`

3. **Undefined Filters**
   - `{{ value|unknown_filter }}`
   - Should suggest similar filter names

4. **Undefined Tests**
   - `{% if value is unknown_test %}`

5. **Complex Templates**
   - Templates with includes/extends
   - Templates with macros
   - Deeply nested blocks

### Test Files

Create `tests/fixtures/templates/` with:
- `valid/` - Valid template examples
- `invalid/` - Templates with various errors
- `edge_cases/` - Tricky but valid templates

## Performance Considerations

- Cache parsed templates during batch validation
- Parse each template only once
- Consider parallel processing for large directories

## Related Issues

- #2 (CLI Tool)
- #6 (Error Reporting)

## References

- [Jinja2 AST documentation](https://jinja.palletsprojects.com/en/stable/api/#ast)
- [Jinja2 custom extensions](https://jinja.palletsprojects.com/en/stable/extensions/)

## Future Enhancements

- Validate against a schema of expected context
- Check for security issues (unsafe filters)
- Performance linting (expensive operations in loops)
- Accessibility checks (alt attributes, etc.)
