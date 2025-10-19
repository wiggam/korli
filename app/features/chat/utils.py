"""Utility functions for chat feature"""

from app.features.chat.state import ChatState
from app.features.chat.schemas import ChatInitializationInput


def create_initial_state(input_data: ChatInitializationInput) -> ChatState:
    """
    Create initial state for a new conversation.
    
    This is a convenience function for API/programmatic use. It prepares
    the state with initialization parameters that will be processed by
    the graph's initialize_state node.
    
    Args:
        input_data: Validated chat initialization parameters
        
    Returns:
        ChatState ready to be passed to the graph
        
    Example:
        >>> from app.features.chat.schemas import ChatInitializationInput
        >>> from app.features.chat.graph import chat_graph
        >>> 
        >>> input_data = ChatInitializationInput(
        ...     student_level="B2",
        ...     foreign_language="Spanish (Spain)",
        ...     native_language="English (US)",
        ...     topic="food and dining"
        ... )
        >>> state = create_initial_state(input_data)
        >>> result = chat_graph.invoke(state)
    """
    return ChatState(
        messages=[],
        summary="",
        topic=input_data.topic,
        student_level=input_data.student_level,
        foreign_language=input_data.foreign_language,
        native_language=input_data.native_language,
        prompt_helper=None  
    )

