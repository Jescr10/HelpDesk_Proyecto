from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api import auth, knowledge_base, system, tickets, users
from app.core.config import settings
from app.core.database import create_session_factory

STATIC = Path(__file__).parent / "static"

def create_app(database_url: str | None = None) -> FastAPI:
    app = FastAPI(title="HelpDesk | Centro de soporte", version="2.0.0")
    app.state.session_factory = create_session_factory(database_url or settings.database_url)
    for router in (system.router, auth.router, users.router, tickets.router, knowledge_base.router):
        app.include_router(router)
    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    @app.get("/", include_in_schema=False)
    def home():
        return FileResponse(STATIC / "index.html")
    return app

app = create_app()
