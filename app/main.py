# app/main.py
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.routes.chat_route import router as chat_router
from app.services.graph_runtime import graph_runtime


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan (startup/shutdown) using an async context manager.
    - On startup: build embedded graph with Postgres checkpointer and store on app.state
    - On shutdown: the context manager closes DB connections cleanly
    """
    db_uri = os.getenv("DATABASE_URL")
    async with graph_runtime(db_uri) as graph:
        app.state.graph = graph
        yield
    # (cleanup handled inside graph_runtime)


app = FastAPI(
    title="Korli Language Learning API",
    description="AI-powered language learning assistant",
    version="1.0.0",
    lifespan=lifespan,
)

# Mount routers
app.include_router(chat_router, prefix="/api", tags=["chat"])


@app.get("/")
async def root():
    return {"message": "Welcome to Korli Language Learning API"}


@app.get("/health")
async def health():
    # optionally verify DB/graph here if you want a deeper healthcheck
    return {"status": "healthy"}
