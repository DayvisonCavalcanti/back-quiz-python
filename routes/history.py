from fastapi import APIRouter, Depends
from models.user import User
from models.history import QuizSubmission, UserHistoryResponse
from services.auth import get_current_user
from services.history import HistoryService
from uuid import UUID

router = APIRouter(
    prefix="/history",
    tags=["History"]
)

@router.post("/submit-quiz")
async def submit_quiz(
    submission: QuizSubmission,
    current_user: User = Depends(get_current_user)
):
    """
    Submete respostas de um quiz
    
    Exemplo de corpo:
    {
        "quiz_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "responses": [
            {
                "question_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
                "selected_option": 0
            }
        ]
    }
    """
    return await HistoryService.submit_quiz_responses(
        UUID(current_user.id), 
        submission
    )

@router.get("/me", response_model=UserHistoryResponse)
async def get_user_history(
    current_user: User = Depends(get_current_user)
):
    """Obtém o histórico completo do usuário"""
    return await HistoryService.get_user_history(UUID(current_user.id))