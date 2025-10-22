# app/services/concurrency.py
from __future__ import annotations
import asyncio
from contextlib import AsyncExitStack
from collections import defaultdict
from typing import Dict

# ---- knobs (tune for your traffic) ----
GLOBAL_LIMIT        = 100   # everything combined
OPENAI_LIMIT        = 20    # LLM + TTS/STT
SUPABASE_LIMIT      = 10    # uploads / list / remove
OTHER_IO_LIMIT      = 30    # e.g., misc HTTP APIs, disk, etc.
PER_USER_AUDIO_LIMIT = 2    # fairness for audio pipelines

# ---- global pools (process-scoped) ----
GLOBAL_SEM   = asyncio.Semaphore(GLOBAL_LIMIT)
OPENAI_SEM   = asyncio.Semaphore(OPENAI_LIMIT)
SUPABASE_SEM = asyncio.Semaphore(SUPABASE_LIMIT)
OTHER_IO_SEM = asyncio.Semaphore(OTHER_IO_LIMIT)

# Optional per-user map (process-scoped)
_per_user_audio: Dict[str, asyncio.Semaphore] = defaultdict(
    lambda: asyncio.Semaphore(PER_USER_AUDIO_LIMIT)
)

class _SemCtx:
    def __init__(self, sem: asyncio.Semaphore): self.sem = sem
    async def __aenter__(self): await self.sem.acquire()
    async def __aexit__(self, *exc): self.sem.release()

class LimitGroup:
    """
    Acquire multiple semaphores in a fixed order to avoid deadlocks:
      GLOBAL -> SERVICE -> (optional) PER-USER
    Usage:
        async with LimitGroup(GLOBAL_SEM, OPENAI_SEM, _per_user_audio[user_id]):
            ...
    """
    def __init__(self, *sems: asyncio.Semaphore):
        self._sems = sems
        self._stack = AsyncExitStack()

    async def __aenter__(self):
        await self._stack.__aenter__()
        for sem in self._sems:
            await self._stack.enter_async_context(_SemCtx(sem))
        return self

    async def __aexit__(self, *exc):
        return await self._stack.__aexit__(*exc)

# Convenience factories (keeps call sites tidy)
def openai_limits(user_id: str | None = None) -> LimitGroup:
    if user_id:
        return LimitGroup(GLOBAL_SEM, OPENAI_SEM, _per_user_audio[user_id])
    return LimitGroup(GLOBAL_SEM, OPENAI_SEM)

def supabase_limits() -> LimitGroup:
    return LimitGroup(GLOBAL_SEM, SUPABASE_SEM)

def other_io_limits() -> LimitGroup:
    return LimitGroup(GLOBAL_SEM, OTHER_IO_SEM)
