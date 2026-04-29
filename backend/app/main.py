from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alerts, health, remediation, reports, ws
from app.core.config import settings
from app.core.logging import configure_logging
from app.services.ollama_client import get_ollama_client


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging(settings.log_level)
    client = get_ollama_client()
    try:
        yield
    finally:
        await client.aclose()


app = FastAPI(
    title="Incident Autopilot",
    description="LLM-powered SOC incident response sandbox",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

app.include_router(health.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(remediation.router, prefix="/api")
app.include_router(ws.router)
