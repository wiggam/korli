"""Graph nodes for chat feature"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage, BaseMessage, AIMessage
from app.services.llm import llm_response, llm_summary, llm_response_correction
from app.features.chat.state import ChatState, CorrectionRecord
from app.features.chat.config import MESSAGES_BEFORE_SUMMARY, MESSAGES_TO_KEEP
from app.features.prompts.chat.prompt_utils import ChatPromptHelper
from app.features.chat.models import LLMTurn, LLMSummary, LLMResponseCorrection
from app.services.language_validation import get_language_greeting, get_language_topic

def generate_initial_question(state: ChatState) -> Dict[str, Any]:
    """
    Generate the opening greeting for the conversation.
    
    Uses pre-defined A1-level greetings from the language map.
    The greeting is simple ("Hello! How are you?") and shown in both
    the student's target (foreign) and native languages.
    """
    prompt_helper: ChatPromptHelper = state["prompt_helper"]
    
    # Build messages specifically for initial question generation
    native_language_greeting: str = get_language_greeting(prompt_helper.native_language)
    foreign_language_greeting: str = get_language_greeting(prompt_helper.foreign_language)
    if state.get("student_level") not in ["A1", "A2"]:
        native_language_greeting = f"{native_language_greeting} {get_language_topic(prompt_helper.native_language)}"
        foreign_language_greeting = f"{foreign_language_greeting} {get_language_topic(prompt_helper.foreign_language)}"

    ai_message = AIMessage(
        content=foreign_language_greeting,
        additional_kwargs={"translation": native_language_greeting}
    )
    
    return {"messages": [ai_message]}

def call_model(state: ChatState) -> Dict[str, Any]:
    """
    Generate a response from the LLM during ongoing conversation.
    
    Stores foreign language in message content, translation in metadata.
    """
    prompt_helper: ChatPromptHelper = state["prompt_helper"]
    summary: str = state.get("summary", "")

    # Build messages with proper system prompt
    if summary:
        # Create summary message using the prompt helper
        summary_message: str = prompt_helper.create_summary_message(summary, len(state["messages"]))
        messages: List[BaseMessage] = [
            SystemMessage(content=prompt_helper.system_prompt),
            HumanMessage(content=summary_message)
        ] + state["messages"]
    else:
        # Regular conversation flow (no summary yet)
        messages: List[BaseMessage] = [
            SystemMessage(content=prompt_helper.system_prompt)
        ] + state["messages"]
    
    for message in messages:
        print(message)
    # Get structured response with both foreign and native language messages
    structured_llm = llm_response().with_structured_output(LLMTurn)
    response: LLMTurn = structured_llm.invoke(messages)
    
    # Store foreign language message with translation in metadata
    ai_message = AIMessage(
        content=response.foreign_language_message,
        additional_kwargs={"translation": response.native_language_message}
    )
    
    return {"messages": [ai_message]}

def should_summarize(state: ChatState) -> bool:
    """
    Check if conversation history needs summarization.
    
    Returns:
        True if message count exceeds threshold, False otherwise
    """
    return len(state["messages"]) > MESSAGES_BEFORE_SUMMARY

def summarize_conversation(state: ChatState) -> Dict[str, Any]:
    """
    Manage conversation history with rolling summaries.
    
    When the history exceeds threshold (configured in config.py):
    1. Keep the most recent messages (MESSAGES_TO_KEEP)
    2. Summarize the older messages in the foreign language
    3. Store summary separately, remove old messages
    """
    prompt_helper: ChatPromptHelper = state["prompt_helper"]
    
    # Split messages: older ones to summarize vs recent ones to keep
    messages_to_summarize = state["messages"][:-MESSAGES_TO_KEEP]
    
    # Get existing summary (if any) to include in the new summary
    existing_summary: str = state.get("summary", "")
    
    # Create summary prompts
    human_summary_prompt: str
    system_summary_prompt: str
    human_summary_prompt, system_summary_prompt = prompt_helper.create_summary_prompts(
        summary_length=len(messages_to_summarize),
        messages_to_summarize=messages_to_summarize,
        existing_summary=existing_summary
    )
    
    # Build messages for summarization
    summary_messages: List[BaseMessage] = [
        SystemMessage(content=system_summary_prompt),
        HumanMessage(content=human_summary_prompt)
    ]
    
    # Get structured summary response
    structured_llm = llm_summary().with_structured_output(LLMSummary)
    response: LLMSummary = structured_llm.invoke(summary_messages)
    
    # Delete the old messages that were summarized
    delete_messages: List[RemoveMessage] = [RemoveMessage(id=m.id) for m in messages_to_summarize]
    
    return {
        "summary": response.summary,
        "messages": delete_messages
    }

def correct_response(state: ChatState) -> Dict[str, Any]:
    prompt_helper: ChatPromptHelper = state["prompt_helper"]
    message: BaseMessage = state["messages"][-1]

    # Create human correction prompt
    human_correction_prompt: str = prompt_helper.create_human_correction_prompt(message)

    # Build messages for response correction
    messages: List[BaseMessage] = [
        SystemMessage(content=prompt_helper.system_correction_prompt),
        HumanMessage(content=human_correction_prompt)
    ]

    # Get structured response correction
    structured_llm = llm_response_correction().with_structured_output(LLMResponseCorrection)
    response: LLMResponseCorrection = structured_llm.invoke(messages)
    
    correction_record: CorrectionRecord = {
        "corrected_message": response.corrected_foreign_language if response.corrected else "",
        "translation": response.native_language_message,
        "corrected": response.corrected,
    }

    return {"corrections": {message.id: correction_record}}
    
