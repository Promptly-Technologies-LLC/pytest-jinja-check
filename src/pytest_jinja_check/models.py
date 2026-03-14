"""Data structures shared across the linter."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class IssueCategory(str, Enum):
    SYNTAX_ERROR = "syntax_error"
    HARDCODED_ROUTE = "hardcoded_route"
    INVALID_ENDPOINT = "invalid_endpoint"
    MISSING_CONTEXT_VAR = "missing_context_variable"


@dataclass
class LintError:
    category: IssueCategory
    message: str
    file: str
    line: Optional[int] = None
    source_file: Optional[str] = None

    def __str__(self) -> str:
        location = self.file
        if self.line is not None:
            location += f":{self.line}"
        if self.source_file:
            location += f" (route in {self.source_file})"
        return f"[{self.category.value}] {location}: {self.message}"


@dataclass
class TemplateInfo:
    """Information extracted from a single Jinja2 template."""

    name: str
    source_path: Path
    variables: set = field(default_factory=set)
    parent_template: Optional[str] = None
    url_for_calls: list = field(default_factory=list)


@dataclass
class RouteContext:
    """A TemplateResponse call found via AST analysis."""

    template_name: str
    context_keys: set = field(default_factory=set)
    source_file: str = ""
    line: int = 0
    function_name: Optional[str] = None
    has_dynamic_context: bool = False
