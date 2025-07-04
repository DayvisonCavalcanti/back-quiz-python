from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class QuizResponse(BaseModel):
    question_id: UUID
    selected_option: int

class QuizSubmission(BaseModel):
    quiz_id: UUID
    responses: List[QuizResponse]

class UserHistoryResponse(BaseModel):
    user_id: UUID
    user_name: str
    user_email: str
    attempts: List[dict]  # Ou defina um modelo mais específico se necessário
    total_quizzes_taken: int
    average_score: float