from fastapi import HTTPException
from datetime import datetime, timezone
from uuid import UUID
from database.supabase_client import supabase
import logging

logger = logging.getLogger(__name__)

class HistoryService:
    @staticmethod
    async def submit_quiz_responses(user_id: UUID, submission):
        try:
            # 1. Obter perguntas do quiz
            questions_response = supabase.table("questions") \
                .select("*") \
                .eq("quiz_id", str(submission.quiz_id)) \
                .execute()
            
            if hasattr(questions_response, 'status_code') and questions_response.status_code >= 400:
                logger.error(f"Supabase error: {questions_response}")
                raise HTTPException(
                    status_code=500,
                    detail="Database error"
                )
                
            questions = questions_response.data
            if not questions:
                raise HTTPException(
                    status_code=404,
                    detail="Quiz não encontrado ou sem perguntas"
                )
            
            # Mapear perguntas
            questions_map = {str(q['id']): q for q in questions}
            
            # 2. Processar respostas
            results = []
            score = 0
            
            for response in submission.responses:
                question_id = str(response.question_id)
                if question_id not in questions_map:
                    continue
                
                question = questions_map[question_id]
                is_correct = response.selected_option == question['correct_option']
                
                if is_correct:
                    score += 1
                
                results.append({
                    "question_id": question_id,
                    "selected_option": response.selected_option,
                    "is_correct": is_correct,
                    "question_text": question['text'],
                    "correct_option": question['correct_option']
                })
            
            # 3. Calcular pontuação
            total_questions = len(results)
            final_score = round((score / total_questions) * 100, 2) if total_questions > 0 else 0
            
            # 4. Salvar tentativa
            attempt_data = {
                "user_id": str(user_id),
                "quiz_id": str(submission.quiz_id),
                "score": final_score,
                "answers": results,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
            
            saved_attempt = supabase.table("quiz_attempts").insert(attempt_data).execute()
            
            if hasattr(saved_attempt, 'status_code') and saved_attempt.status_code >= 400:
                logger.error(f"Supabase error: {saved_attempt}")
                raise HTTPException(
                    status_code=500,
                    detail="Database error"
                )
                
            return {
                "score": final_score,
                "total_questions": total_questions,
                "correct_answers": score,
                "details": results
            }
            
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.error(f"Error submitting quiz: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )

    @staticmethod
    async def get_user_history(user_id: UUID):
        try:
            # 1. Obter dados do usuário
            user_response = supabase.table("users") \
                .select("name, email") \
                .eq("id", str(user_id)) \
                .execute()
            
            if hasattr(user_response, 'status_code') and user_response.status_code >= 400:
                logger.error(f"Supabase error: {user_response}")
                raise HTTPException(
                    status_code=500,
                    detail="Database error"
                )
                
            if not user_response.data:
                raise HTTPException(
                    status_code=404,
                    detail="Usuário não encontrado"
                )
                
            user_data = user_response.data[0]
            
            # 2. Obter tentativas
            attempts_response = supabase.table("quiz_attempts") \
                .select("*") \
                .eq("user_id", str(user_id)) \
                .order("completed_at", desc=True) \
                .execute()
            
            if hasattr(attempts_response, 'status_code') and attempts_response.status_code >= 400:
                logger.error(f"Supabase error: {attempts_response}")
                raise HTTPException(
                    status_code=500,
                    detail="Database error"
                )
                
            attempts = attempts_response.data
            
            # 3. Calcular estatísticas
            total_quizzes = len(attempts)
            avg_score = sum(a['score'] for a in attempts) / total_quizzes if total_quizzes > 0 else 0
            
            return {
                "user_id": str(user_id),
                "user_name": user_data['name'],
                "user_email": user_data['email'],
                "attempts": attempts,
                "total_quizzes_taken": total_quizzes,
                "average_score": round(avg_score, 2)
            }
            
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.error(f"Error fetching history: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )