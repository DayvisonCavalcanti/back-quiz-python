from fastapi import HTTPException
from database.supabase_client import supabase
from models.quiz import QuizWithQuestions
import logging
from uuid import UUID, uuid4
from datetime import datetime

logger = logging.getLogger(__name__)

class QuizService:
    @staticmethod
    def create_quiz_with_questions(quiz_data: QuizWithQuestions, creator_id: UUID):
        try:
            # Gerar novo UUID para o quiz
            quiz_id = str(uuid4())
            
            # 1. Criar o quiz
            quiz_dict = {
                "id": quiz_id,
                "title": quiz_data.title,
                "creator_id": str(creator_id),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Adicionar campos opcionais
            if quiz_data.description is not None:
                quiz_dict["description"] = quiz_data.description
            if quiz_data.category is not None:
                quiz_dict["category"] = quiz_data.category
                
            # Inserir quiz no banco
            quiz_response = supabase.table("quizzes").insert(quiz_dict).execute()
            
            # Verificar erro
            if hasattr(quiz_response, 'status_code') and quiz_response.status_code >= 400:
                logger.error(f"Supabase quiz error: {quiz_response}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Database error: {quiz_response.text}"
                )
                
            if not quiz_response.data:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create quiz"
                )
            
            # 2. Preparar e inserir perguntas
            questions_to_insert = []
            for question in quiz_data.questions:
                # Validação de opção correta
                if question.correct_option >= len(question.options):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid correct option for question: {question.text}"
                    )
                
                questions_to_insert.append({
                    "text": question.text,
                    "options": question.options,
                    "correct_option": question.correct_option,
                    "quiz_id": quiz_id
                })
            
            # Inserir todas as perguntas
            questions_response = supabase.table("questions").insert(questions_to_insert).execute()
            
            # Verificar erro
            if hasattr(questions_response, 'status_code') and questions_response.status_code >= 400:
                # Rollback - remover o quiz criado
                supabase.table("quizzes").delete().eq("id", quiz_id).execute()
                logger.error(f"Supabase questions error: {questions_response}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Database error: {questions_response.text}"
                )
                
            if not questions_response.data:
                # Rollback
                supabase.table("quizzes").delete().eq("id", quiz_id).execute()
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create questions"
                )
            
            return {
                "quiz_id": quiz_id,
                "title": quiz_data.title,
                "created_questions": len(questions_response.data),
                "questions": questions_response.data
            }
            
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.error(f"Error creating quiz with questions: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )

    @staticmethod
    def get_quiz(quiz_id: str):
        try:
            response = supabase.table("quizzes").select("*").eq("id", quiz_id).execute()
            
            if hasattr(response, 'status_code') and response.status_code >= 400:
                logger.error(f"Supabase error: {response}")
                return None
                
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching quiz: {str(e)}")
            return None