"""Graph nodes for chat feature"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage, BaseMessage, AIMessage
from app.services.llm import llm_response, llm_summary, llm_validation, llm_response_correction
from app.features.chat.state import ChatState, CorrectionRecord
from app.features.chat.config import MESSAGES_BEFORE_SUMMARY, MESSAGES_TO_KEEP
from app.features.prompts.chat.prompt_utils import ChatPromptHelper
from app.features.chat.models import LLMTurn, LLMSummary, LLMTopicValidation, LLMResponseCorrection


def generate_initial_question(state: ChatState) -> Dict[str, Any]:
    """
    Generate the opening question for the conversation.
    
    Stores foreign language in message content, translation in metadata.
    """
    prompt_helper: ChatPromptHelper = state["prompt_helper"]
    
    # Build messages specifically for initial question generation
    messages: List[BaseMessage] = [
        SystemMessage(content=prompt_helper.system_prompt),
        HumanMessage(content=prompt_helper.human_initial_prompt)
    ]
    
    # Get structured response with both foreign and native language messages
    structured_llm = llm_response().with_structured_output(LLMTurn)
    response: LLMTurn = structured_llm.invoke(messages)
    
    # Store foreign language message with translation in metadata
    ai_message = AIMessage(
        content=response.foreign_language_message,
        additional_kwargs={"translation": response.native_language_message}
    )
    
    return {"messages": [ai_message]}

def validate_topic(state: ChatState) -> Dict[str, Any]:
    """
    Validate and cleanse the user-provided topic.
    
    Runs after initialize_state, so prompt_helper is available.
    
    Validates that the topic is:
    - Legal
    - Not hateful or extremist
    - Not sexually explicit
    - Intelligible (not random words)
    
    Returns:
        Updated state with validated topic and valid_topic flag.
        If valid: topic is updated to cleaned version
        If invalid: valid_topic is set to False
    """
    prompt_helper: ChatPromptHelper = state["prompt_helper"]

    # Build messages for topic validation using prompt_helper
    messages: List[BaseMessage] = [
        SystemMessage(content=prompt_helper.cleanse_topic_system_prompt),
        HumanMessage(content=prompt_helper.cleanse_topic_human_prompt)
    ]
    
    # Get structured validation response
    structured_llm = llm_validation().with_structured_output(LLMTopicValidation)
    response: LLMTopicValidation = structured_llm.invoke(messages)

    # Return validation result
    if response.valid_topic:
        # Topic is valid - update to cleaned version
        return {
            "topic": response.lightly_cleaned_topic,
            "valid_topic": True
        }
    else:
        # Topic is invalid - just set flag
        return {
            "valid_topic": False
        }

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
    
