from __future__ import annotations

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router)
app.include_router(workflow_router)
