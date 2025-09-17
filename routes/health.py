from fastapi import APIRouter
from src.services.predictor import get_model_status

router = APIRouter()


@router.get("/health")
def health():
    """Health check endpoint"""
    status_info = get_model_status()
    return {
        "status": "ok", 
        "model_loaded": status_info["model_loaded"], 
        "model_version": status_info["model_version"]
    }


@router.get("/metadata")
def metadata():
    """Metadata endpoint"""
    return get_model_status()
