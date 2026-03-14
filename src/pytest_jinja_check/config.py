"""Configuration loading from pyproject.toml."""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]


@dataclass
class LinterConfig:
    """Configuration for the template linter."""

    template_dir: str = "templates"
    python_dir: str = "."
    route_file_patterns: list = field(default_factory=lambda: ["**/*.py"])
    ignore_variables: set = field(
        default_factory=lambda: {"request", "url_for", "get_flashed_messages"}
    )
    allowed_url_prefixes: list = field(
        default_factory=lambda: [
            "#",
            "http://",
            "https://",
            "mailto:",
            "tel:",
            "javascript:",
            "data:",
        ]
    )
    hardcoded_route_ignore_attrs: set = field(
        default_factory=lambda: {"src", "poster", "data"}
    )
    root: Path = field(default_factory=Path.cwd)


def load_config(root: Optional[Path] = None) -> LinterConfig:
    """Load configuration from pyproject.toml if present."""
    if root is None:
        root = Path.cwd()

    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return LinterConfig(root=root)

    with open(pyproject, "rb") as f:
        data = tomllib.load(f)

    tool_config = data.get("tool", {}).get("pytest-jinja-check", {})
    if not tool_config:
        return LinterConfig(root=root)

    config = LinterConfig(root=root)
    if "template_dir" in tool_config:
        config.template_dir = tool_config["template_dir"]
    if "python_dir" in tool_config:
        config.python_dir = tool_config["python_dir"]
    if "route_file_patterns" in tool_config:
        config.route_file_patterns = tool_config["route_file_patterns"]
    if "ignore_variables" in tool_config:
        config.ignore_variables = set(tool_config["ignore_variables"])
    if "allowed_url_prefixes" in tool_config:
        config.allowed_url_prefixes = tool_config["allowed_url_prefixes"]
    if "hardcoded_route_ignore_attrs" in tool_config:
        config.hardcoded_route_ignore_attrs = set(
            tool_config["hardcoded_route_ignore_attrs"]
        )

    return config
