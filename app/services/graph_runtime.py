# app/services/graph_runtime.py
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.features.chat.graph import chat_graph


@asynccontextmanager
async def graph_runtime(database_url: str | None = None) -> AsyncIterator:
    """
    Async context manager that:
      1) Opens an AsyncPostgresSaver from a connection string
      2) Calls .setup() (idempotent) to ensure tables exist
      3) Attaches the checkpointer to your already-compiled graph (with Langfuse callbacks)
      4) Yields the ready-to-use embedded graph
      5) Cleans up the checkpointer on shutdown

    Usage:
        async with graph_runtime(os.getenv("DATABASE_URL")) as graph:
            await graph.ainvoke(...)

    Notes:
      - Langfuse callbacks are defined in app.features.chat.graph (chat_graph).
      - We only attach the checkpointer here (infra concern).
    """
    dsn = database_url or os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL environment variable is not set.")

    saver_cm = AsyncPostgresSaver.from_conn_string(dsn)
    checkpointer = await saver_cm.__aenter__()
    try:
        await checkpointer.setup()
        # Preserve callbacks configured in graph.py; add checkpointer at runtime.
        embedded_graph = chat_graph.with_config({"checkpointer": checkpointer})
        yield embedded_graph
    finally:
        # Ensure connections are closed cleanly on shutdown
        await saver_cm.__aexit__(None, None, None)
