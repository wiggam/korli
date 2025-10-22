"""
Shared Supabase Upload Utility

This module provides a unified Supabase upload function that can be used by 
all audio services (Google TTS, OpenAI TTS, etc.) to avoid code duplication.
"""

from __future__ import annotations

import os
import asyncio
from typing import Optional

import aiohttp
from asyncio import timeout as aio_timeout
from tenacity import (
    retry, stop_after_attempt, wait_exponential, retry_if_exception_type
)

from ..http_utils import create_tcp_connector

# ───────────────────────────────────────
# Config & Constants
# ───────────────────────────────────────

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
BUCKET_NAME = "audio-bucket"

REQUEST_TIMEOUT = 30
MAX_RETRIES = 5

# ───────────────────────────────────────
# Global aiohttp session
# ───────────────────────────────────────

_session: Optional[aiohttp.ClientSession] = None

def _get_session() -> aiohttp.ClientSession:
    """Lazily constructs or returns the global aiohttp session."""
    global _session
    if _session is None or _session.closed:
        connector = create_tcp_connector()
        _session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        )
    return _session

async def close_session() -> None:
    """Gracefully close the aiohttp session at shutdown."""
    global _session
    if _session and not _session.closed:
        await _session.close()
    _session = None

# ───────────────────────────────────────
# Supabase upload helper
# ───────────────────────────────────────

@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=1, max=6),
    retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
)
async def upload_audio_to_supabase(audio_bytes: bytes, filename: str, *, upsert: bool = False) -> str:
    """
    Uploads audio file to Supabase and returns a URL.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY")

    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{filename}"
    headers = {
        # New keys: use the Secret key on the server
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,  # recommended for REST calls
        "Content-Type": "audio/mpeg",
        "Cache-Control": "public, max-age=31536000",
    }
    if upsert:
        headers["x-upsert"] = "true"

    session = _get_session()
    async with aio_timeout(REQUEST_TIMEOUT):
        async with session.put(url, data=audio_bytes, headers=headers) as resp:
            if not (200 <= resp.status < 300):
                error_text = await resp.text()
                raise RuntimeError(f"Supabase upload failed ({resp.status}): {error_text}")


    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{filename}"


# ───────────────────────────────────────
# Test / Demo
# ───────────────────────────────────────

if __name__ == "__main__":
    """
    Test script: Generate audio using OpenAI TTS and upload to Supabase.
    
    Usage:
        python -m app.services.audio.supabase_upload
    """
    import sys
    from datetime import datetime
    from .openai_audio import generate_speech, close_session as close_tts_session
    
    async def test_tts_and_upload():
        """Generate speech and upload to Supabase."""
        print("=" * 60)
        print("OpenAI TTS + Supabase Upload Test")
        print("=" * 60)
        
        try:
            # Step 1: Generate audio using OpenAI TTS
            test_text = "Очень хорошо! Ты голоден? Что будешь есть?"
            print(f"\n📝 Generating speech from text:")
            print(f"   Text: {test_text[:50]}...")
            print(f"   Voice: alloy")
            print(f"   Model: tts-1")
            
            audio_bytes = await generate_speech(
                text=test_text,
                voice="ash",
                model="tts-1-hd",
                speed=1.0
            )
            
            print(f"✅ Audio generated successfully! Size: {len(audio_bytes)} bytes")
            
            # Step 2: Upload to Supabase
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_tts_{timestamp}.mp3"
            
            print(f"\n☁️  Uploading to Supabase...")
            print(f"   Filename: {filename}")
            print(f"   Bucket: {BUCKET_NAME}")
            
            public_url = await upload_audio_to_supabase(audio_bytes, filename)
            
            print(f"✅ Upload successful!")
            print(f"\n🔗 Public URL:")
            print(f"   {public_url}")
            
            # Step 3: Summary
            print(f"\n" + "=" * 60)
            print("✨ Test completed successfully!")
            print("=" * 60)
            print(f"• Audio size: {len(audio_bytes)} bytes")
            print(f"• Filename: {filename}")
            print(f"• URL: {public_url}")
            
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            # Clean up sessions
            print(f"\n🧹 Cleaning up sessions...")
            await close_session()
            await close_tts_session()
            print("✅ Sessions closed")
    
    # Run the test
    asyncio.run(test_tts_and_upload()) 