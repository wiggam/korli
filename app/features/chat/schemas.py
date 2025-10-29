from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from app.services.language_validation import validate_language

# Define valid student levels (CEFR framework)
StudentLevel = Literal["A1", "A2", "B1", "B2", "C1", "C2"]


class ChatInitializationInput(BaseModel):
    """
    Input validation for initializing a new chat conversation.
    
    This model validates the required parameters for starting a language
    learning conversation. The graph uses these to:
    - Set the conversation difficulty level
    - Configure language-specific prompts
    - Generate appropriate greetings and responses
    """
    
    student_level: StudentLevel = Field(
        ...,
        description="CEFR language proficiency level (A1=Beginner, C2=Proficient)"
    )
    
    foreign_language: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Language the student is learning (e.g., 'Spanish (Spain)', 'French')"
    )
    
    native_language: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Student's native language for translations (e.g., 'English (US)')"
    )
    
    tutor_gender: Optional[Literal["male", "female"]] = Field(
        default="female",
        description="Preferred tutor gender (affects voice selection for audio)"
    )
    
    @field_validator('foreign_language', 'native_language')
    @classmethod
    def validate_language_support(cls, v: str) -> str:
        """Validate that the language is supported by the system"""
        return validate_language(v)

    class Config:
        json_schema_extra = {
            "example": {
                "student_level": "B2",
                "foreign_language": "Spanish (Spain)",
                "native_language": "English (US)",
                "tutor_gender": "female"
            }
        }

