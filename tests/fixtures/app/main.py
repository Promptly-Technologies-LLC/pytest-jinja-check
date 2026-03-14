"""Sample FastAPI app for testing the linter."""

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "title": "Home", "heading": "Welcome", "items": []},
    )


@app.get("/about")
async def about(request: Request):
    # Intentionally missing 'title' variable
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/contact")
async def contact(request: Request):
    return templates.TemplateResponse(
        request, "home.html", context={"title": "Contact", "heading": "Contact Us", "items": []}
    )
