"""Tests for configuration loading."""

from pytest_jinja_check.config import load_config


class TestLoadConfig:
    def test_auto_check_defaults_to_false(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text(
            '[tool.pytest-jinja-check]\ntemplate_dir = "templates"\n'
        )
        config = load_config(tmp_path)
        assert config.auto_check is False

    def test_loads_auto_check(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text(
            "[tool.pytest-jinja-check]\nauto_check = true\n"
        )
        config = load_config(tmp_path)
        assert config.auto_check is True

    def test_loads_app_import_path(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text(
            '[tool.pytest-jinja-check]\napp = "myapp.main:app"\n'
        )
        config = load_config(tmp_path)
        assert config.app == "myapp.main:app"
