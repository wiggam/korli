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
    reasoning: str = Field(
        ...,
        description="The reasoning for the response in English"
    )

class LLMSummary(BaseModel):
    """Summary of the conversation for context management"""
    summary: str

class LLMResponseCorrection(BaseModel):
    """Correction of the response of the student"""
    corrected_foreign_language: str = Field(..., description="The corrected message in the foreign language, or an empty string if the response was correct")
    native_language_message: str = Field(..., description="The corrected message in the native language")
    corrected: bool = Field(..., description="True if the response was corrected, False otherwise")