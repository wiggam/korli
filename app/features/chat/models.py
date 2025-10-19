from pydantic import BaseModel, Field
from typing import List
from langchain_core.messages import BaseMessage

class LLMTurn(BaseModel):
    """Represents one tutor response with both languages:
    - foreign_language_message: message in the student's target language
    - native_language_message: translation in the student's native language
    """

    foreign_language_message: str = Field(
        ...,
        description="Your response in the student's target language"
    )
    native_language_message: str = Field(
        ...,
        description="The same message translated into the student's native language"
    )

class LLMSummary(BaseModel):
    """Summary of the conversation for context management"""
    summary: str

class LLMTopicValidation(BaseModel):
    """Validation of the topic of the conversation"""
    lightly_cleaned_topic: str = Field(..., description="A lightly-cleaned version of the topic")
    valid_topic: bool = Field(..., description="True if the topic is valid, False otherwise")

class LLMResponseCorrection(BaseModel):
    """Correction of the response of the student"""
    corrected_foreign_language: str = Field(..., description="The corrected message in the foreign language, or an empty string if the response was correct")
    native_language_message: str = Field(..., description="The corrected message in the native language")
    corrected: bool = Field(..., description="True if the response was corrected, False otherwise")