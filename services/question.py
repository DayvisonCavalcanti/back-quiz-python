from fastapi import HTTPException
from database.supabase_client import supabase
from models.question import Question
import logging

logger = logging.getLogger(__name__)

class QuestionService:
    @staticmethod
    def create_question(question_data: dict) -> Question:
        try:
            # Validação de opções
            if not isinstance(question_data["options"], list) or len(question_data["options"]) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="Question must have at least 2 options"
                )
            
            # Validação de opção correta
            if question_data["correct_option"] < 0 or question_data["correct_option"] >= len(question_data["options"]):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid correct option index"
                )
            
            # Preparar dados
            processed_data = {
                "text": str(question_data["text"]),
                "options": question_data["options"],
                "correct_option": int(question_data["correct_option"]),
                "quiz_id": str(question_data["quiz_id"])
            }
            
            # Inserir no banco
            response = supabase.table("questions").insert(processed_data).execute()
            
            # Nova verificação de erro
            if hasattr(response, 'status_code') and response.status_code >= 400:
                logger.error(f"Supabase error: {response}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Database error: {response.text}"
                )
                
            if not response.data:
                logger.error("No data returned from insertion")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create question"
                )
                
            return Question(**response.data[0])
            
        except KeyError as e:
            logger.error(f"Missing field: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Database error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Error creating question"
            )