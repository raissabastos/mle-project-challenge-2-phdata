"""
Aplicação FastAPI para predição de preços de casas
"""
import traceback
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from src.config.settings import APP_TITLE
from src.services.predictor import load_artifacts
from src.utils.logger import setup_logger
from routes import health, predict

# Setup logger
logger = setup_logger()

# Create FastAPI app
app = FastAPI(title=APP_TITLE)

# Allow CORS during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(predict.router)


@app.on_event("startup")
def startup_event():
    """Carrega artefatos na inicialização da aplicação"""
    load_artifacts()


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handler para erros de validação"""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
        content={"detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para erros gerais"""
    logger.error(f"Unhandled exception: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500, 
        content={"detail": "Internal server error"}
    )