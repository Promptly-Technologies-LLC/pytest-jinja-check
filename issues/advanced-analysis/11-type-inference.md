---
title: Type inference from template usage
labels: enhancement, type-checking, advanced
milestone: v0.3.0
priority: P2
---

## Description

Infer variable types from how they're used in templates and optionally validate against type annotations or Pydantic models.

## Goals

- Infer types from template usage patterns
- Generate TypedDict or Pydantic models
- Validate context against inferred/declared types
- Export JSON Schema (jinja2schema compatibility)

## User Story

**As a developer**, I want to know what types my template variables should be, so I can catch type errors before runtime and generate accurate type hints for my code.

## Type Inference Rules

### Scalar Types

```html
<!-- String: Used in text context -->
{{ username }}
{{ "Hello " + name }}
→ username: str, name: str

<!-- Number: Used in arithmetic -->
{{ count + 1 }}
{{ price * 0.1 }}
→ count: int, price: float

<!-- Boolean: Used in conditionals -->
{% if is_active %}
{% if not is_deleted %}
→ is_active: bool, is_deleted: bool
```

### Object/Dict Access

```html
<!-- Object with attributes -->
{{ user.name }}
{{ user.email }}
→ user: {'name': str, 'email': str}

<!-- Nested objects -->
{{ user.profile.avatar_url }}
→ user: {'profile': {'avatar_url': str}}
```

### Lists/Arrays

```html
<!-- List iteration -->
{% for item in items %}
  {{ item.name }}
{% endfor %}
→ items: List[{'name': str}]

<!-- List operations -->
{{ items|length }}
{{ items|first }}
→ items: List[Any]
```

### Filters Hint Types

```html
<!-- String filters -->
{{ name|upper }}
{{ email|lower }}
→ name: str, email: str

<!-- Number filters -->
{{ price|round }}
→ price: float

<!-- Date filters -->
{{ created_at|strftime("%Y-%m-%d") }}
→ created_at: datetime
```

### Tests Hint Types

```html
<!-- Type tests -->
{% if value is string %}
{% if count is number %}
{% if items is iterable %}
→ Can infer types from tests
```

## Implementation

### Type Inference Engine

```python
from typing import Any, Dict, List, Set, Union
from dataclasses import dataclass
from jinja2 import nodes, Environment

@dataclass
class TypeInfo:
    """Information about a variable's inferred type."""
    name: str
    inferred_type: str
    confidence: float  # 0.0 to 1.0
    usage_examples: List[str]
    line_numbers: List[int]

class TypeInferrer:
    """
    Infer types from Jinja2 template usage.

    Uses Jinja2 AST to analyze how variables are used
    and infer their types.
    """

    def __init__(self):
        self.types: Dict[str, TypeInfo] = {}

    def infer_from_template(self, template_path: Path) -> Dict[str, TypeInfo]:
        """
        Infer types from template file.

        Returns:
            Dictionary of variable names to TypeInfo
        """
        with open(template_path) as f:
            source = f.read()

        env = Environment()
        ast = env.parse(source)

        # Walk AST and infer types
        self._walk_ast(ast)

        return self.types

    def _walk_ast(self, node):
        """Walk AST and infer types from usage."""
        if isinstance(node, nodes.Name):
            self._infer_from_name(node)
        elif isinstance(node, nodes.Getattr):
            self._infer_from_getattr(node)
        elif isinstance(node, nodes.Filter):
            self._infer_from_filter(node)
        elif isinstance(node, nodes.Test):
            self._infer_from_test(node)

        # Recurse to children
        for child in node.iter_child_nodes():
            self._walk_ast(child)

    def _infer_from_getattr(self, node: nodes.Getattr):
        """
        Infer type from attribute access.

        {{ user.name }} → user has attribute 'name'
        """
        # Get base object name
        if isinstance(node.node, nodes.Name):
            obj_name = node.node.name
            attr_name = node.attr

            if obj_name not in self.types:
                self.types[obj_name] = TypeInfo(
                    name=obj_name,
                    inferred_type='object',
                    confidence=0.8,
                    usage_examples=[],
                    line_numbers=[]
                )

            # Add attribute to object type
            # Store as: {'attr1': str, 'attr2': int, ...}
            # (Simplified for example)

    def _infer_from_filter(self, node: nodes.Filter):
        """
        Infer type from filter usage.

        {{ name|upper }} → name is string
        {{ items|length }} → items is list/collection
        """
        filter_type_hints = {
            'upper': 'str',
            'lower': 'str',
            'capitalize': 'str',
            'title': 'str',
            'length': 'list',
            'first': 'list',
            'last': 'list',
            'sum': 'list[number]',
            'round': 'float',
            'int': 'number',
            'float': 'number',
        }

        filter_name = node.name
        if filter_name in filter_type_hints:
            # Apply type hint to filtered variable
            pass

    def _infer_from_test(self, node: nodes.Test):
        """
        Infer type from test usage.

        {% if value is string %} → value might be string
        """
        test_type_hints = {
            'string': 'str',
            'number': 'number',
            'iterable': 'list',
            'mapping': 'dict',
        }
        # Apply hints based on test
```

### TypedDict Generation

```python
from typing import TypedDict

def generate_typed_dict(types: Dict[str, TypeInfo]) -> str:
    """
    Generate TypedDict from inferred types.

    Args:
        types: Inferred type information

    Returns:
        Python code for TypedDict

    Example:
        class ProfileContext(TypedDict):
            username: str
            email: str
            is_admin: bool
    """
    lines = []
    lines.append("from typing import TypedDict\n")
    lines.append("class TemplateContext(TypedDict):")

    for var_name, type_info in sorted(types.items()):
        python_type = _convert_to_python_type(type_info.inferred_type)
        lines.append(f"    {var_name}: {python_type}")

    return "\n".join(lines)

def _convert_to_python_type(inferred: str) -> str:
    """Convert inferred type to Python type hint."""
    type_map = {
        'string': 'str',
        'number': 'int',
        'float': 'float',
        'bool': 'bool',
        'list': 'List[Any]',
        'object': 'Dict[str, Any]',
    }
    return type_map.get(inferred, 'Any')
```

### Pydantic Model Generation

```python
def generate_pydantic_model(types: Dict[str, TypeInfo]) -> str:
    """
    Generate Pydantic model from inferred types.

    Example:
        from pydantic import BaseModel

        class ProfileContext(BaseModel):
            username: str
            email: str
            is_admin: bool = False
    """
    lines = []
    lines.append("from pydantic import BaseModel\n")
    lines.append("class TemplateContext(BaseModel):")

    for var_name, type_info in sorted(types.items()):
        python_type = _convert_to_python_type(type_info.inferred_type)

        # Optional if confidence is low
        if type_info.confidence < 0.7:
            python_type = f"Optional[{python_type}] = None"

        lines.append(f"    {var_name}: {python_type}")

    return "\n".join(lines)
```

### JSON Schema Export

```python
def generate_json_schema(types: Dict[str, TypeInfo]) -> dict:
    """
    Generate JSON Schema from inferred types.

    Compatible with jinja2schema output format.
    """
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {},
        "required": []
    }

    for var_name, type_info in types.items():
        schema["properties"][var_name] = {
            "type": _to_json_schema_type(type_info.inferred_type)
        }

        if type_info.confidence > 0.8:
            schema["required"].append(var_name)

    return schema
```

## CLI Integration

### Generate Types Command

```bash
# Generate TypedDict
jinja2-validator infer-types template.html --format typeddict

# Generate Pydantic model
jinja2-validator infer-types template.html --format pydantic

# Generate JSON Schema
jinja2-validator infer-types template.html --format json-schema

# Output to file
jinja2-validator infer-types template.html --format pydantic -o context_models.py
```

### Example Output

```python
# Generated by jinja2-validator
from typing import TypedDict, List

class ProfileContext(TypedDict):
    """Context for templates/profile.html"""
    username: str  # Used at line 12, 45
    email: str  # Used at line 18
    is_admin: bool  # Used at line 30
    posts: List[dict]  # Used at line 50
```

## Type Validation

### Validate Against TypedDict

```python
from typing import TypedDict, get_type_hints

def validate_context_types(context: dict, type_class: type) -> List[str]:
    """
    Validate context against TypedDict.

    Returns:
        List of type mismatch error messages
    """
    errors = []
    hints = get_type_hints(type_class)

    for key, expected_type in hints.items():
        if key not in context:
            errors.append(f"Missing key: {key}")
            continue

        value = context[key]
        if not isinstance(value, expected_type):
            errors.append(
                f"Type mismatch for '{key}': "
                f"expected {expected_type}, got {type(value)}"
            )

    return errors
```

### Validate Against Pydantic

```python
from pydantic import BaseModel, ValidationError

def validate_with_pydantic(context: dict, model: type[BaseModel]):
    """
    Validate context with Pydantic model.

    Raises:
        ValidationError: If context doesn't match model
    """
    try:
        model(**context)
    except ValidationError as e:
        # Pretty print validation errors
        for error in e.errors():
            print(f"Validation error: {error}")
        raise
```

## Testing

```python
def test_infer_string_type():
    template = "{{ username|upper }}"
    types = infer_types_from_string(template)
    assert types['username'].inferred_type == 'str'

def test_infer_object_type():
    template = "{{ user.name }}"
    types = infer_types_from_string(template)
    assert types['user'].inferred_type == 'object'
    assert 'name' in types['user'].attributes

def test_infer_list_type():
    template = "{% for item in items %}{{ item.name }}{% endfor %}"
    types = infer_types_from_string(template)
    assert types['items'].inferred_type == 'list'

def test_generate_typeddict():
    types = {
        'username': TypeInfo('username', 'str', 1.0, [], []),
        'email': TypeInfo('email', 'str', 1.0, [], []),
    }
    code = generate_typed_dict(types)
    assert 'username: str' in code
    assert 'TypedDict' in code
```

## Acceptance Criteria

- [ ] Infer basic scalar types (str, int, float, bool)
- [ ] Infer object/dict types with attributes
- [ ] Infer list types
- [ ] Track confidence levels
- [ ] Generate TypedDict code
- [ ] Generate Pydantic model code
- [ ] Generate JSON Schema
- [ ] CLI command for type inference
- [ ] Validate context against types
- [ ] Comprehensive tests
- [ ] Documentation with examples

## Future Enhancements

- [ ] Learn from existing type hints in code
- [ ] Inter-template type inference (includes/extends)
- [ ] Generic type support (List[User])
- [ ] Union types (str | int)
- [ ] Literal types ("admin" | "user")
- [ ] IDE integration (type hints in editor)

## Related Issues

- #7 (Runtime Validation)
- #12 (JSON Schema Export)

## References

- jinja2schema: https://github.com/aromanovich/jinja2schema
- Python typing module: https://docs.python.org/3/library/typing.html
- Pydantic: https://docs.pydantic.dev/
- JSON Schema: https://json-schema.org/
