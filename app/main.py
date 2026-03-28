"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import routes
from app.core.config import settings
from app.core.logging import (
    bind_log_context,
    clear_log_context,
    configure_logging,
    get_logger,
)

configure_logging(settings.log_level, json_logs=settings.log_json)
logger = get_logger(__name__)


def run_alembic_upgrade() -> None:
    """Run Alembic migrations to head. Called before the app serves."""
    root = Path(__file__).resolve().parent.parent
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "alembic"))
    command.upgrade(config, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("startup_migrations_begin")
        run_alembic_upgrade()
        # Alembic's fileConfig can clobber logging — restore ours
        configure_logging(settings.log_level, json_logs=settings.log_json)
        logger.info("startup_migrations_complete")
    except Exception:
        logger.exception("startup_migrations_failed")
        raise

    logger.info("startup_complete")
    yield
    logger.info("shutdown_complete")


app = FastAPI(
    title="Slidely PPT Generator",
    description="Agent-based presentation generation service",
    lifespan=lifespan,
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log every incoming request and outgoing response."""
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    started_at = perf_counter()

    clear_log_context()
    bind_log_context(request_id=request_id)

    method = request.method
    path = request.url.path
    query = str(request.url.query) if request.url.query else ""
    client = request.client.host if request.client else "-"

    logger.info(f">>> {method} {path}", query=query, client=client)

    try:
        response = await call_next(request)
        duration_ms = round((perf_counter() - started_at) * 1000, 2)

        log = logger.error if response.status_code >= 500 else (
            logger.warning if response.status_code >= 400 else logger.info
        )
        log(f"<<< {method} {path} {response.status_code} {duration_ms}ms")

        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as exc:
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        logger.exception(
            f"<<< {method} {path} ERROR {duration_ms}ms — {type(exc).__name__}: {exc}",
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "request_id": request_id},
            headers={"X-Request-ID": request_id},
        )
    finally:
        clear_log_context()


app.include_router(routes.router)
