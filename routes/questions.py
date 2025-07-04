from fastapi import APIRouter, Depends, HTTPException
from models.question import Question, QuestionBatch
from models.user import User
from services.auth import get_current_user
from services.question import QuestionService
from services.quiz import QuizService
import logging
from uuid import UUID
from typing import List

# Cria a instância do router
router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)
logger = logging.getLogger(__name__)

@router.post("/batch", response_model=List[Question], status_code=201)
async def create_questions_batch(
    batch: QuestionBatch,
    current_user: User = Depends(get_current_user)
):
    """
    Cria múltiplas perguntas associadas a um quiz
    
    Args:
        batch: Dados do lote de perguntas (quiz_id + lista de perguntas)
        current_user: Usuário autenticado
    
    Returns:
        List[Question]: Lista de perguntas criadas com seus IDs
    
    Raises:
        HTTPException: 400 - Se os dados forem inválidos
                     403 - Se o usuário não for o criador do quiz
                     404 - Se o quiz não for encontrado
    """
    try:
        # Verifica se o quiz existe e pertence ao usuário
        quiz = QuizService.get_quiz(str(batch.quiz_id))
        if str(quiz.creator_id) != str(current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Você não tem permissão para adicionar perguntas a este quiz"
            )
        
        # Processa cada pergunta do lote
        created_questions = []
        for question_data in batch.questions:
            # Cria um dicionário com todos os dados necessários
            full_question = {
                "text": question_data.text,
                "options": question_data.options,
                "correct_option": question_data.correct_option,
                "quiz_id": str(batch.quiz_id)  # Convertemos para string
            }
            
            # Valida se o índice da opção correta é válido
            if question_data.correct_option >= len(question_data.options) or question_data.correct_option < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Índice da opção correta inválido para pergunta: {question_data.text}"
                )
            
            # Cria a pergunta
            question = QuestionService.create_question(full_question)
            created_questions.append(question)
        
        return created_questions

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro ao criar lote de perguntas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar lote de perguntas"
        )