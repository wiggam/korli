import os
import dotenv
from typing import Optional
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Defaults (override via env)
_DEFAULT_MODEL      = os.getenv("STRONG_MODEL")
_RESPONSE_MODEL     = os.getenv("STRONG_MODEL")      
_SUMMARY_MODEL      = os.getenv("FAST_MODEL")       
_VALIDATION_MODEL   = os.getenv("FAST_MODEL")    
_RESPONSE_CORRECTION_MODEL = os.getenv("FAST_MODEL")    

def get_llm(model: Optional[str] = None, **kwargs) -> ChatOpenAI:
    """
    Factory for ChatOpenAI with sensible defaults. 
    Pass model=... to override per call, or rely on env-configured task getters below.
    Extra OpenAI params (temperature, timeout, etc.) can be passed via **kwargs.
    """
    return ChatOpenAI(
        model=model or _DEFAULT_MODEL,
        api_key=_OPENAI_API_KEY,
        **kwargs
    )

def llm_response(**kwargs) -> ChatOpenAI:
    """Model for main conversational responses."""
    return get_llm(_RESPONSE_MODEL, **kwargs)

def llm_summary(**kwargs) -> ChatOpenAI:
    """Model for summarization."""
    return get_llm(_SUMMARY_MODEL, **kwargs)

def llm_response_correction(**kwargs) -> ChatOpenAI:
    """Model for response correction."""
    return get_llm(_RESPONSE_CORRECTION_MODEL, **kwargs)