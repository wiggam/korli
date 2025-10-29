"""Utility functions for chat feature"""

from typing import Dict, Any
from app.features.chat.schemas import ChatInitializationInput


def create_initial_state(input_data: ChatInitializationInput) -> Dict[str, Any]:
    """
    Convert validated input parameters to initial graph state.
    
    This convenience function transforms the validated ChatInitializationInput
    into a state dict that can be passed to the chat graph. The graph's
    initialize_state node will handle creating the prompt_helper and setting
    up the conversation.
    
    Args:
        input_data: Validated chat initialization parameters
        
    Returns:
        Initial state dict ready for graph invocation
        
    Example:
        >>> from app.features.chat.schemas import ChatInitializationInput
        >>> from app.features.chat.graph import chat_graph
        >>> 
        >>> # Create and validate input
        >>> input_data = ChatInitializationInput(
        ...     student_level="B2",
        ...     foreign_language="Spanish (Spain)",
        ...     native_language="English (US)",
        ...     tutor_gender="female"
        ... )
        >>> 
        >>> # Convert to state and invoke graph
        >>> initial_state = create_initial_state(input_data)
        >>> result = await chat_graph.ainvoke(
        ...     initial_state,
        ...     config={"configurable": {"thread_id": thread_id}}
        ... )
        
    Note:
        - The graph's initialize_state node will create the prompt_helper
        - For continuing conversations, just pass messages directly to the graph
        - The state dict only includes the minimal initialization parameters
    """
    return {
        "student_level": input_data.student_level,
        "foreign_language": input_data.foreign_language,
        "native_language": input_data.native_language,
        "tutor_gender": input_data.tutor_gender,
        "messages": [],  # Empty for new conversation
    }

