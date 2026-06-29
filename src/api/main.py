from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.product_routes import router as product_router
from src.api.workflow_routes import router as workflow_router
from src.database.session import initialize_product_database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    initialize_product_database()
    yield


app = FastAPI(
    title="NVIDIA Startup AI Radar API",
    description="Product API for persisted startup analysis, recommendations, dossiers, and exports.",
    version="0.1.0",
    lifespan=lifespan,
)


def _cors_origins() -> list[str]:
    configured = os.environ.get("CORS_ALLOWED_ORIGINS", "").strip()
    app_mode = os.environ.get("APP_MODE", "product").casefold()
    if configured:
        origins = [origin.strip() for origin in configured.split(",") if origin.strip()]
    elif app_mode == "product":
        origins = []
    else:
        origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
    if app_mode == "product" and "*" in origins:
        msg = "APP_MODE=product does not allow wildcard CORS origins."
        raise RuntimeError(msg)
    return origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router)
app.include_router(workflow_router)
