from pydantic import BaseModel, Field, field_validator
from typing import Literal
from app.services.language_validation import validate_language

# Define valid student levels
StudentLevel = Literal["A1", "A2", "B1", "B2", "C1", "C2"]

class ChatInitializationInput(BaseModel):
    """Input validation for chat initialization"""
    
    student_level: StudentLevel = Field(
        ...,
        description="CEFR language proficiency level"
    )
    
    foreign_language: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Language the student is learning"
    )
    
    native_language: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Student's native language"
    )
    
    topic: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Topic for the conversation lesson"
    )
    
    @field_validator('foreign_language', 'native_language')
    @classmethod
    def validate_language_support(cls, v: str) -> str:
        """Validate that language is supported"""
        return validate_language(v)
    
    @field_validator('lesson_topic')
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Validate and clean the lesson topic"""
        topic = v.strip()
        if not topic:
            raise ValueError("Lesson topic cannot be empty")
        return topic

    class Config:
        json_schema_extra = {
            "example": {
                "student_level": "B2",
                "foreign_language": "Spanish (Spain)",
                "native_language": "English (US)",
                "lesson_topic": "food and dining"
            }
        }

