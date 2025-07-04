from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from models.question import QuestionBase

class QuizWithQuestions(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    questions: List[QuestionBase] = Field(..., min_items=1)

    class Config:
        schema_extra = {
            "example": {
                "title": "Quiz de Matemática",
                "description": "Perguntas sobre matemática básica",
                "category": "Matemática",
                "questions": [
                    {
                        "text": "Quanto é 5 × 6?",
                        "options": ["30", "25", "36", "35"],
                        "correct_option": 0
                    }
                ]
            }
        }