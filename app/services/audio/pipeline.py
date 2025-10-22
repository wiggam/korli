# app/services/audio/pipeline.py
from __future__ import annotations
from typing import Optional, Literal, Dict
from datetime import datetime, timezone
import uuid
from .openai_audio import generate_speech
from .supabase_upload import upload_audio_to_supabase

Storage = Literal["supabase", "memory", "none"]

async def generate_audio(
    *,
    text: str,
    voice: str = "alloy",
    model: str = "gpt-4o-mini-tts",
    speed: float = 1.0,
    storage: Storage = "none",
    filename_prefix: str = "tts",
    thread_id: Optional[str] = None,
    upsert: bool = False,
) -> Dict[str, Optional[str]]:
    """
    Returns:
      {
        "url": str | None,      # e.g. Supabase public URL
        "b64": str | None,      # base64 for in-memory delivery (optional)
        "bytes_len": int,       # diagnostic
      }
    """
    audio_bytes = await generate_speech(text=text, voice=voice, model=model, speed=speed)

    if storage == "supabase":
        # Create unique filename: timestamp + UUID for guaranteed uniqueness
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        
        # Organize by thread_id if provided (creates folder structure in Supabase)
        if thread_id:
            filename = f"{thread_id}/{filename_prefix}_{ts}_{unique_id}.mp3"
        else:
            filename = f"{filename_prefix}_{ts}_{unique_id}.mp3"
            
        url = await upload_audio_to_supabase(audio_bytes, filename, upsert=upsert)
        return {"url": url, "b64": None, "bytes_len": len(audio_bytes)}

    if storage == "memory":
        # If you prefer pushing bytes/base64 to the client directly:
        import base64
        return {"url": None, "b64": base64.b64encode(audio_bytes).decode("ascii"), "bytes_len": len(audio_bytes)}

    # storage == "none": caller decides what to do with raw bytes (e.g., WebSocket stream)
    return {"url": None, "b64": None, "bytes_len": len(audio_bytes)}
