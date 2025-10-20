"""
Audio Services Module
---------------------
Provides TTS, STT, and Supabase upload functionality.
"""

from .openai_audio import generate_speech, transcribe_audio, close_session
from .supabase_upload import upload_audio_to_supabase

__all__ = [
    "generate_speech",
    "transcribe_audio", 
    "upload_audio_to_supabase",
    "close_session",
]

