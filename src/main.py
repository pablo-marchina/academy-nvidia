"""Minimal FastAPI application scaffold."""

from fastapi import FastAPI

app = FastAPI(title="NVIDIA Startup AI Radar")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    """Basic health endpoint for local validation."""

    return {"status": "ok"}
