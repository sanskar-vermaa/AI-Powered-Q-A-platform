import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.config import DEFAULT_SECRET_KEY, get_settings
from app.database import init_db
from app.routers import (
    admin,
    ai,
    answers,
    auth,
    bookmarks,
    chat,
    comments,
    moderation,
    notifications,
    questions,
    stats,
    tags,
    users,
    votes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if get_settings().secret_key == DEFAULT_SECRET_KEY:
        logger.warning("SECRET_KEY is not set; using an insecure development key")
    init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="Community Q&A with AI-generated answers, an AI assistant, reputation and moderation.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for module in (
        auth,
        users,
        questions,
        answers,
        votes,
        comments,
        tags,
        bookmarks,
        notifications,
        moderation,
        admin,
        ai,
        chat,
        stats,
    ):
        app.include_router(module.router)

    @app.get("/api/health", tags=["meta"])
    def health():
        return {"status": "ok", "version": __version__}

    _mount_frontend(app, Path(settings.frontend_dist))
    return app


def _mount_frontend(app: FastAPI, dist: Path) -> None:
    """Serve the built React app (if present) with client-side routing fallback."""
    index = dist / "index.html"
    if not index.is_file():
        return
    if (dist / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        candidate = (dist / path).resolve()
        if path and candidate.is_file() and dist.resolve() in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(index)


app = create_app()
