# app/audio/openai_tts_stt_service.py
"""
Async OpenAI TTS & Whisper v3 Service
--------------------------------------
- TTS: Generates speech from text using OpenAI's TTS API.
- STT: Transcribes short voice clips (≤25 s) to text.
- Optionally caches the raw audio + transcript to Supabase.
- Concurrency-safe: one global aiohttp.ClientSession + semaphore.

Typical use:
-------------
# TTS
audio_bytes = await generate_speech(text="Hello world", voice="alloy")

# STT
text = await transcribe_audio(audio_bytes, lang_code="ru")

Close the session with `await close_session()` at shutdown.
"""

from __future__ import annotations

import os, asyncio
from typing import Optional, Union

import aiohttp
from asyncio import timeout as aio_timeout
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..http_utils import create_tcp_connector
from .config import TTS_MODEL, STT_MODEL

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
REQUEST_TIMEOUT = 30
MAX_RETRIES     = 5
CONCURRENCY_LIMIT = 20

_session: Optional[aiohttp.ClientSession] = None
STT_SEM = asyncio.Semaphore(CONCURRENCY_LIMIT)


def _get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        connector = create_tcp_connector()
        _session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        )
    return _session


async def close_session() -> None:
    global _session
    if _session and not _session.closed:
        await _session.close()
    _session = None


# ───────────────────────────────────────
# TTS (Text-to-Speech)
# ───────────────────────────────────────

@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=1, max=6),
    retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
)
async def _tts_generate(text: str,
                        voice: str = "alloy",
                        model: str = TTS_MODEL,
                        speed: float = 1.0,
                        instructions: Optional[str] = None) -> bytes:
    """Calls OpenAI TTS API and returns audio bytes."""
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,  # tts-1, tts-1-hd, or gpt-4o-mini-tts
        "input": text,
        "voice": voice,  # alloy, echo, fable, onyx, nova, shimmer
        "speed": speed   # 0.25 to 4.0
    }
    
    # Add instructions parameter (only supported by gpt-4o-mini-tts)
    if instructions is not None:
        payload["instructions"] = instructions
    
    async with aio_timeout(REQUEST_TIMEOUT):
        async with _get_session().post(url, headers=headers, json=payload) as r:
            if r.status != 200:
                raise RuntimeError(f"OpenAI TTS {r.status}: {await r.text()}")
            return await r.read()


async def generate_speech(
    text: str,
    *,
    voice: str = "alloy",
    model: str = TTS_MODEL,
    speed: float = 1.0,
    instructions: Optional[str] = None
) -> bytes:
    """
    Generate speech audio from text using OpenAI TTS.
    
    Parameters
    ----------
    text : str
        The text to convert to speech
    voice : str
        Voice to use: alloy, echo, fable, onyx, nova, shimmer
    model : str
        Model to use: tts-1 (faster), tts-1-hd (higher quality), or gpt-4o-mini-tts (with instructions)
    speed : float
        Speed of speech (0.25 to 4.0, default 1.0)
    instructions : str, optional
        Instructions for controlling speech characteristics (only supported by gpt-4o-mini-tts).
        Examples: "Speak in a cheerful and positive tone", "Use a British accent", 
        "Whisper softly", "Speak with excitement"
        
    Returns
    -------
    bytes
        MP3 audio data
    """
    async with STT_SEM:
        return await _tts_generate(text, voice=voice, model=model, speed=speed, instructions=instructions)


# ───────────────────────────────────────
# STT (Speech-to-Text)
# ───────────────────────────────────────

@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=1, max=6),
    retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
)
async def _whisper(bytes_data: bytes,
                   lang_code: str | None = None,
                   prompt: str | None = None,
                   model: str = STT_MODEL) -> str:
    """Calls Whisper-v3 API and returns plain text."""
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

    form = aiohttp.FormData()
    form.add_field("model", model)
    form.add_field("file", bytes_data,
                   filename="speech.mp3",
                   content_type="audio/mpeg")
    if lang_code: form.add_field("language", lang_code)
    if prompt:    form.add_field("prompt", prompt)

    async with aio_timeout(REQUEST_TIMEOUT):
        async with _get_session().post(url, headers=headers, data=form) as r:
            if r.status != 200:
                raise RuntimeError(f"Whisper {r.status}: {await r.text()}")
            data = await r.json()
            return data["text"]


async def transcribe_audio(
    audio: bytes,
    *,
    lang_code: str | None = None,
    prompt: str | None = None
) -> str:
    """Public helper: wraps semaphore + whisper call."""
    async with STT_SEM:
        return await _whisper(audio, lang_code=lang_code, prompt=prompt)
