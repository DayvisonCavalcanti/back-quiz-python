from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes.users import router as users_router
from routes.auth import router as auth_router
from routes.quizzes import router as quizzes_router
from routes.questions import router as questions_router
from routes.history import router as history_router
import logging

app = FastAPI()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(quizzes_router)
app.include_router(questions_router)
app.include_router(history_router)

@app.get("/")
async def root():
    return {"message": "API Online"}

# Middleware para tratamento de erros
@app.middleware("http")
async def catch_exceptions(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )