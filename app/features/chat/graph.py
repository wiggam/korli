"""LangGraph workflow for chat conversations"""

from typing import Literal, Dict, Any
from langgraph.graph import StateGraph, END, START
from app.features.chat.state import ChatState
from app.features.prompts.chat.prompt_utils import ChatPromptHelper
from app.features.chat.nodes import (
    generate_initial_question,
    call_model,
    should_summarize,
    summarize_conversation,
    correct_response
)


def initialize_state(state: ChatState) -> Dict[str, Any]:
    """
    Initialize node: Set up prompt_helper if not already initialized.
    
    This node checks if the state needs initialization (new conversation)
    and creates the prompt_helper from the input parameters.
    
    For new conversations via LangGraph Studio, provide:
    - student_level: CEFR level (A1, A2, B1, B2, C1, C2)
    - foreign_language: Language being learned
    - native_language: Student's native language
    
    Returns:
        Updated state with initialized prompt_helper
    """
    # Check if already initialized (has prompt_helper)
    if state.get("prompt_helper") is not None:
        return {}  # Already initialized, no changes needed
    
    # Get initialization parameters from state
    student_level = state.get("student_level", "B2")
    foreign_language = state.get("foreign_language", "Spanish (Spain)")
    native_language = state.get("native_language", "English (US)")
    
    # Create prompt helper
    prompt_helper = ChatPromptHelper(
        student_level=student_level,
        foreign_language=foreign_language,
        native_language=native_language,
    )
    
    # Return initialized state
    return {
        "prompt_helper": prompt_helper,
        "summary": state.get("summary", ""),
        "correction_buffer": {} 
    }

def route_after_init(state: ChatState) -> Literal["generate_initial_question", "call_model"]:
    """
    Route after initialization based on conversation state.
    
    Returns:
        - "generate_initial_question" if new conversation (no messages)
        - "call_model" if ongoing conversation (has messages)
    """
    has_messages = len(state.get("messages", [])) > 0
    
    if has_messages:
        return "continue_conversation"
    
    return "generate_initial_question"

def fanout_after_init(state: ChatState) -> Dict[str, Any]:
    # No state changes; existence of edges below triggers both branches
    return {}

def fanin_after_processing(state: ChatState) -> Dict[str, Any]:
    # No state changes; existence of edges below triggers both branches
    return {}


def create_chat_graph():
    """
    Create and compile the chat conversation graph.
    
    This graph uses ASYNC nodes for LLM operations, enabling concurrent
    request handling and better API performance.
    
    Graph Flow:
    
    New Conversation:
    1. START -> initialize_state (set up prompt_helper)
    2. initialize_state -> generate_initial_question (async - generates opening question)
    3. -> END
    
    Ongoing Conversation:
    1. START -> initialize_state (already has prompt_helper)
    2. initialize_state -> fanout_after_init (fan-out point)
    3. Parallel execution:
       - call_model (async - generate AI response)
       - correct_response (async - correct user's previous message)
    4. Both converge -> fanin_after_processing
    5. fanin_after_processing -> check if summarization needed
       - If yes: summarize_conversation (async) -> END
       - If no: END
    
    Usage:
        # Async invocation (recommended for APIs)
        result = await chat_graph.ainvoke(input_state)
        
        # Streaming (async)
        async for event in chat_graph.astream(input_state):
            print(event)
    
    Returns:
        Compiled StateGraph ready for async invocation
    """
    # Initialize the graph with ChatState
    workflow = StateGraph(ChatState)
    
    # Add nodes
    workflow.add_node("initialize_state", initialize_state)
    workflow.add_node("generate_initial_question", generate_initial_question)
    workflow.add_node("fanout_after_init", fanout_after_init)
    workflow.add_node("correct_response", correct_response)
    workflow.add_node("call_model", call_model)
    workflow.add_node("fanin_after_processing", fanin_after_processing)
    workflow.add_node("summarize_conversation", summarize_conversation)
    
    # Set entry point to initialization
    workflow.add_edge(START, "initialize_state")
    
    # After initialization, route to validation or model based on conversation state
    workflow.add_conditional_edges(
        "initialize_state",
        route_after_init,
        {
            "generate_initial_question": "generate_initial_question",
            "continue_conversation": "fanout_after_init"
        }
    )
    
    # After generating initial question, end (return to user for response)
    workflow.add_edge("generate_initial_question", END)
    
    # After init fan out - respond and correct user response in parallel
    workflow.add_edge("fanout_after_init", "call_model")
    workflow.add_edge("fanout_after_init", "correct_response")

    # Both branches converge on apply_correction
    workflow.add_edge("call_model", "fanin_after_processing")
    workflow.add_edge("correct_response", "fanin_after_processing")
    
    # After applying correction, check if we need to summarize
    workflow.add_conditional_edges(
        "fanin_after_processing",
        should_summarize,
        {
            True: "summarize_conversation",   # Need to summarize
            False: END                        # No summary needed, return to user
        }
    )
    
    # After summarization, end (return to user for next response)
    workflow.add_edge("summarize_conversation", END)
    
    # Compile the graph (Langfuse SDK tracing is added in nodes.py)
    return workflow.compile()


# Create the compiled graph instance
chat_graph = create_chat_graph()
