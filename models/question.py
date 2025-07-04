from pydantic import BaseModel, Field, validator
from typing import List, Optional
from uuid import UUID

class QuestionBase(BaseModel):
    text: str = Field(..., min_length=5)
    options: List[str] = Field(..., min_items=2)
    correct_option: int = Field(..., ge=0)

    @validator('correct_option')
    def validate_correct_option(cls, v, values):
        if 'options' in values and v >= len(values['options']):
            raise ValueError("Correct option index out of range")
        return v

class QuestionCreateWithoutQuiz(QuestionBase):
    """Versão sem quiz_id para uso no batch"""
    pass

class QuestionCreate(QuestionBase):
    """Versão completa com quiz_id para criação individual"""
    quiz_id: UUID

class QuestionUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=5)
    options: Optional[List[str]] = Field(None, min_items=2)
    correct_option: Optional[int] = Field(None, ge=0)

    @validator('correct_option')
    def validate_correct_option(cls, v, values):
        if v is not None and 'options' in values and values['options'] is not None:
            if v >= len(values['options']) or v < 0:
                raise ValueError("Correct option index out of range")
        return v

class Question(QuestionBase):
    id: UUID
    quiz_id: UUID

    class Config:
        from_attributes = True

class QuestionBatch(BaseModel):
    quiz_id: UUID
    questions: List[QuestionCreateWithoutQuiz]