from fastapi import APIRouter, Depends, HTTPException
from models.quiz import QuizWithQuestions
from models.user import User
from services.quiz import QuizService
from services.auth import get_current_user
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/quizzes",
    tags=["Quizzes"]
)

@router.post("/with-questions", status_code=201)
async def create_quiz_with_questions(
    quiz_data: QuizWithQuestions,
    current_user: User = Depends(get_current_user)
):
    """
    Cria um quiz completo com todas as perguntas em uma única requisição
    
    Exemplo de corpo:
    {
        "title": "Quiz de Matemática",
        "description": "Teste seus conhecimentos",
        "category": "Matemática",
        "questions": [
            {
                "text": "Quanto é 5 × 6?",
                "options": ["30", "25", "36", "35"],
                "correct_option": 0
            }
        ]
    }
    """
    try:
        # Converter ID do usuário para UUID
        user_uuid = UUID(current_user.id)
        return QuizService.create_quiz_with_questions(quiz_data, user_uuid)
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to create quiz"
        )