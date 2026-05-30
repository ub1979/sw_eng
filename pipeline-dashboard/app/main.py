from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings, VERSION
from app.database import init_database
from app.orchestrator import Orchestrator
from app.routers.api import router as api_router
from app.routers.sse import router as sse_router


class SecurityHeadersMiddleware:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def wrapped_send(message):
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                headers.append((b"x-content-type-options", b"nosniff"))
                headers.append((b"x-frame-options", b"DENY"))
                headers.append((b"referrer-policy", b"strict-origin-when-cross-origin"))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, wrapped_send)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    orch = Orchestrator()
    await orch.on_startup()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="SDLC Pipeline Dashboard",
        version=VERSION,
        docs_url="/docs" if settings.env == "dev" else None,
        redoc_url="/redoc" if settings.env == "dev" else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    app.add_middleware(SecurityHeadersMiddleware)

    app.include_router(api_router)
    app.include_router(sse_router)

    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/")
    async def root():
        return FileResponse("static/index.html")

    return app


app = create_app()
