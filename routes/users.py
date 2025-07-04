from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User, UserCreate
from services.auth import get_current_user, get_current_admin
from services.user import UserService
import logging

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    return await UserService.create_user(user_data)

@router.get("/me", response_model=User)
async def get_current_user_endpoint(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.get("/admin/me", response_model=User)
async def get_current_admin_endpoint(
    current_admin: User = Depends(get_current_admin)
):
    return current_admin