"""Tests for Python AST route analysis."""

from pathlib import Path

from pytest_jinja_check.route_analysis import (
    extract_all_route_contexts,
    extract_route_contexts,
)


SAMPLE_SOURCE_OLD_API = '''\
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "title": "Home", "items": []},
    )

@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})
'''

SAMPLE_SOURCE_NEW_API = '''\
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request, "home.html", context={"title": "Home", "items": []}
    )
'''

SAMPLE_SOURCE_KEYWORD_API = '''\
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="home.html", context={"title": "Home"}
    )
'''

SAMPLE_SOURCE_DYNAMIC = '''\
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    ctx = build_context()
    return templates.TemplateResponse("home.html", ctx)
'''

SAMPLE_SOURCE_SPREAD = '''\
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    base = {"request": request}
    return templates.TemplateResponse("home.html", {**base, "title": "Home"})
'''


class TestExtractRouteContextsOldAPI:
    def test_extracts_template_names(self):
        contexts = extract_route_contexts(SAMPLE_SOURCE_OLD_API, "app.py")
        names = [c.template_name for c in contexts]
        assert "home.html" in names
        assert "about.html" in names

    def test_extracts_context_keys(self):
        contexts = extract_route_contexts(SAMPLE_SOURCE_OLD_API, "app.py")
        home = next(c for c in contexts if c.template_name == "home.html")
        assert "request" in home.context_keys
        assert "title" in home.context_keys
        assert "items" in home.context_keys

    def test_extracts_function_name(self):
        contexts = extract_route_contexts(SAMPLE_SOURCE_OLD_API, "app.py")
        home = next(c for c in contexts if c.template_name == "home.html")
        assert home.function_name == "home"

    def test_extracts_source_info(self):
        contexts = extract_route_contexts(SAMPLE_SOURCE_OLD_API, "app.py")
        assert all(c.source_file == "app.py" for c in contexts)
        assert all(c.line > 0 for c in contexts)


class TestExtractRouteContextsNewAPI:
    def test_new_positional_api(self):
        contexts = extract_route_contexts(SAMPLE_SOURCE_NEW_API, "app.py")
        assert len(contexts) == 1
        c = contexts[0]
        assert c.template_name == "home.html"
        assert "title" in c.context_keys
        assert "items" in c.context_keys

    def test_keyword_api(self):
        contexts = extract_route_contexts(SAMPLE_SOURCE_KEYWORD_API, "app.py")
        assert len(contexts) == 1
        c = contexts[0]
        assert c.template_name == "home.html"
        assert "title" in c.context_keys


class TestExtractRouteContextsDynamic:
    def test_flags_dynamic_context(self):
        contexts = extract_route_contexts(SAMPLE_SOURCE_DYNAMIC, "app.py")
        assert len(contexts) == 1
        assert contexts[0].has_dynamic_context

    def test_spread_extracts_literal_keys(self):
        contexts = extract_route_contexts(SAMPLE_SOURCE_SPREAD, "app.py")
        assert len(contexts) == 1
        c = contexts[0]
        assert "title" in c.context_keys
        assert c.has_dynamic_context  # because of **base


class TestExtractAllRouteContexts:
    def test_scans_fixture_app(self, app_dir):
        contexts = extract_all_route_contexts(app_dir)
        names = [c.template_name for c in contexts]
        assert "home.html" in names
        assert "about.html" in names
