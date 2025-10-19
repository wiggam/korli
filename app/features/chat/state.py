from typing import TypedDict, Annotated, Optional, Any, Dict
from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState, add_messages
from app.features.prompts.chat.prompt_utils import ChatPromptHelper


class CorrectionRecord(TypedDict, total=False):
    corrected_message: str          # final foreign-language text (corrected or same as original)
    translation: str                # translation of corrected_message
    changed: bool                   # whether a change was applied


class ChatState(MessagesState):
    """
    Chat state for language learning conversations.
    
    summary: Summary of older messages for context management
    topic: Current conversation topic
    valid_topic: Whether the topic passed validation (None = not yet validated)
    correction_buffer: Temporary buffer for correction data before applying
    prompt_helper: Helper for generating prompts (arbitrary Python object)
    student_level: Student's CEFR level (for initialization)
    foreign_language: Language being learned (for initialization)
    native_language: Student's native language (for initialization)
    """
    # Initialization parameters (used to create prompt_helper)
    student_level: Optional[str]
    foreign_language: Optional[str]
    native_language: Optional[str]
    
    # Core state
    summary: str
    prompt_helper: Optional[Any]
    corrections: Dict[str, CorrectionRecord]
    
