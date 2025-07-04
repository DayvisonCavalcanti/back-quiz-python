from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from models.user import User
from services.auth import AuthService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/token")
async def login(request: Request):
    try:
        # Aceita tanto form-data quanto JSON
        content_type = request.headers.get('Content-Type')
        
        if content_type == "application/x-www-form-urlencoded":
            form_data = await request.form()
            username = form_data.get("username")
            password = form_data.get("password")
        elif content_type == "application/json":
            json_data = await request.json()
            username = json_data.get("username")
            password = json_data.get("password")
        else:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported media type"
            )
        
        if not username or not password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Username and password are required"
            )
        
        user = await AuthService.authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = AuthService.create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )