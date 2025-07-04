from fastapi import HTTPException, status
from models.user import User, UserCreate
from database.supabase_client import supabase
from services.password import PasswordService
from typing import Optional
from datetime import datetime
import logging
from uuid import UUID

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        try:
            response = supabase.table("users").select("*").eq("email", email).execute()
            
            if hasattr(response, 'status_code') and response.status_code >= 400:
                logger.error(f"Supabase error: {response}")
                return None
                
            if not response.data:
                return None
                
            user_data = response.data[0]
            return User(
                id=str(user_data['id']),
                email=user_data['email'],
                name=user_data['name'],
                hashed_password=user_data['hashed_password'],
                is_admin=user_data.get('is_admin', False),
                created_at=datetime.fromisoformat(user_data['created_at']),
                last_login=datetime.fromisoformat(user_data['last_login']) if user_data.get('last_login') else None
            )
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao buscar usuário"
            )

    @staticmethod
    async def create_user(user_data: UserCreate) -> User:
        try:
            existing_user = await UserService.get_user_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já cadastrado"
                )
                
            hashed_password = PasswordService.get_password_hash(user_data.password)
            
            new_user_data = {
                "email": user_data.email,
                "name": user_data.name,
                "hashed_password": hashed_password,
                "is_admin": user_data.is_admin,
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = supabase.table("users").insert(new_user_data).execute()
            
            if hasattr(response, 'status_code') and response.status_code >= 400:
                logger.error(f"Supabase error: {response}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro ao criar usuário no banco"
                )
                
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro ao criar usuário - nenhum dado retornado"
                )
                
            created_user = response.data[0]
            return User(
                id=str(created_user['id']),
                email=created_user['email'],
                name=created_user['name'],
                hashed_password=created_user['hashed_password'],
                is_admin=created_user['is_admin'],
                created_at=datetime.fromisoformat(created_user['created_at']),
                last_login=None
            )
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao criar usuário"
            )