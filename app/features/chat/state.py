from typing import TypedDict, Annotated, Optional, Any, Dict, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState, add_messages
from app.features.prompts.chat.prompt_utils import ChatPromptHelper


def preserve_existing(existing: Optional[Any], new: Optional[Any]) -> Optional[Any]:
    """
    Reducer that preserves existing value if new value is None.
    
    This ensures initialization parameters aren't lost when omitted from
    subsequent requests. Only the first request needs to provide these values;
    LangGraph's checkpointer will persist them for the thread.
    
    Args:
        existing: Current value from the checkpoint
        new: New value from the incoming state update
        
    Returns:
        new if new is not None, otherwise existing
    """
    return new if new is not None else existing


class CorrectionRecord(TypedDict, total=False):
    corrected_message: str          # final foreign-language text (corrected or same as original)
    translation: str                # translation of corrected_message
    corrected: bool                 # whether a change was applied
    audio_url: Optional[str]        # Supabase URL of correction audio (if corrected)


class ChatState(MessagesState):
    """
    State management for language learning conversations.
    
    Inherits from MessagesState (provides 'messages' field with message history).
    
    Fields:
        messages: Conversation history (inherited from MessagesState)
        student_level: Student's CEFR proficiency level (A1-C2)
        foreign_language: Target language being learned
        native_language: Student's native language for translations
        tutor_gender: Tutor gender preference (affects audio voice selection)
        student_gender: Student's gender (for personalization, if needed)
        summary: Rolling summary of older messages for context management
        prompt_helper: Helper object for generating language-specific prompts
        corrections: Dict mapping message IDs to their correction records
    
    Note:
        Fields annotated with preserve_existing reducer will retain their values
        across requests when not explicitly provided. This means you only need to
        send initialization parameters (student_level, languages, etc.) on the
        first request - subsequent requests will automatically use the persisted values.
    """
    # Initialization parameters (persist across requests with custom reducer)
    student_level: Annotated[Optional[str], preserve_existing]
    foreign_language: Annotated[Optional[str], preserve_existing]
    native_language: Annotated[Optional[str], preserve_existing]
    tutor_gender: Annotated[Optional[Literal["male", "female"]], preserve_existing]
    student_gender: Annotated[Optional[Literal["male", "female"]], preserve_existing]
    
    # Core state (also persisted)
    summary: str
    prompt_helper: Annotated[Optional[Any], preserve_existing]
    corrections: Dict[str, CorrectionRecord]
    
