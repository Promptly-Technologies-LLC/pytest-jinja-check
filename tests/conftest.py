from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TEMPLATES_DIR = FIXTURES_DIR / "templates"
APP_DIR = FIXTURES_DIR / "app"


@pytest.fixture
def templates_dir():
    return TEMPLATES_DIR


@pytest.fixture
def app_dir():
    return APP_DIR
