"""AST-based extraction of TemplateResponse calls from Python source files."""

import ast
from pathlib import Path
from typing import Optional

from .models import RouteContext


class _TemplateResponseVisitor(ast.NodeVisitor):
    """Walk a Python AST to find TemplateResponse calls."""

    def __init__(self, filename: str):
        self.filename = filename
        self.calls: list[RouteContext] = []
        self._current_function: Optional[str] = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        old = self._current_function
        self._current_function = node.name
        self.generic_visit(node)
        self._current_function = old

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node: ast.Call) -> None:
        func_name = self._get_call_name(node)
        if func_name and "TemplateResponse" in func_name:
            template_name = self._extract_template_name(node)
            context_keys, has_dynamic = self._extract_context_keys(node)
            if template_name:
                self.calls.append(
                    RouteContext(
                        template_name=template_name,
                        context_keys=context_keys,
                        source_file=self.filename,
                        line=node.lineno,
                        function_name=self._current_function,
                        has_dynamic_context=has_dynamic,
                    )
                )
        self.generic_visit(node)

    @staticmethod
    def _get_call_name(node: ast.Call) -> Optional[str]:
        """Get the name of the called function (e.g. 'templates.TemplateResponse')."""
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
        elif isinstance(node.func, ast.Name):
            return node.func.id
        return None

    @staticmethod
    def _extract_template_name(node: ast.Call) -> Optional[str]:
        """Extract the template name from a TemplateResponse call.

        Handles both old API (name as first arg) and new API (request first, name second
        or name as keyword).
        """
        # Check keyword argument 'name'
        for kw in node.keywords:
            if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                return kw.value.value

        # Positional args
        if node.args:
            # Old API: first arg is string template name
            if isinstance(node.args[0], ast.Constant) and isinstance(
                node.args[0].value, str
            ):
                return node.args[0].value
            # New API: first arg is request, second arg is template name
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                if isinstance(node.args[1].value, str):
                    return node.args[1].value

        return None

    @staticmethod
    def _extract_context_keys(node: ast.Call) -> tuple[set, bool]:
        """Extract context dict keys from a TemplateResponse call.

        Returns (keys, has_dynamic_context).
        """
        dict_node = None
        has_dynamic = False

        # Check 'context' keyword
        for kw in node.keywords:
            if kw.arg == "context" and isinstance(kw.value, ast.Dict):
                dict_node = kw.value
                break

        # Check positional args for a dict
        if dict_node is None:
            for arg in node.args:
                if isinstance(arg, ast.Dict):
                    dict_node = arg
                    break
                # Non-dict, non-constant positional arg could be a variable holding context
                if not isinstance(arg, ast.Constant) and not isinstance(
                    arg, ast.Name
                ):
                    continue

        if dict_node is None:
            # Check if any positional arg is a variable (could be context dict)
            for arg in node.args:
                if isinstance(arg, ast.Name) and arg.id != "request":
                    has_dynamic = True
            return (set(), has_dynamic)

        keys = set()
        for key in dict_node.keys:
            if key is None:
                # **spread operator — can't resolve statically
                has_dynamic = True
            elif isinstance(key, ast.Constant):
                keys.add(key.value)

        return (keys, has_dynamic)


def extract_route_contexts(source: str, filename: str = "<unknown>") -> list[RouteContext]:
    """Parse Python source and extract all TemplateResponse calls."""
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError:
        return []

    visitor = _TemplateResponseVisitor(filename)
    visitor.visit(tree)
    return visitor.calls


def extract_all_route_contexts(
    python_dir: Path,
    file_patterns: Optional[list[str]] = None,
) -> list[RouteContext]:
    """Scan Python files for TemplateResponse calls.

    Args:
        python_dir: Root directory to search
        file_patterns: Glob patterns for files to scan (default: ["**/*.py"])
    """
    if file_patterns is None:
        file_patterns = ["**/*.py"]

    python_dir = Path(python_dir)
    all_contexts = []

    seen_files: set[Path] = set()
    for pattern in file_patterns:
        for path in sorted(python_dir.glob(pattern)):
            if path in seen_files or not path.is_file():
                continue
            seen_files.add(path)

            source = path.read_text()
            relative = str(path.relative_to(python_dir))
            all_contexts.extend(extract_route_contexts(source, relative))

    return all_contexts
