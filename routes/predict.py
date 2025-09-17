from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from interfaces.schemas import PredictRequest
from src.services.predictor import predict_prices, explain_permutation_importance
from src.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger()


@router.post("/predict", response_model=Dict[str, Any])
def predict(request: PredictRequest):
    """
    Endpoint for house price prediction.
    Accepts a list of houses and returns predictions for each one.
    The model uses basic house features and automatically enriches with demographic data from provided zipcode.
    
    Args:
        request: PredictRequest object containing list of houses for prediction
        
    Returns:
        - predictions: List of predictions with price, index and confidence
        - model_version: Version of the model
        - n_predictions: Number of predictions made
        - latency_seconds: Processing time in seconds
        - request_id: uuid of the request
        - timestamp: Timestamp of the request
        
    Example:
        POST /predict
        {
            "instances": [
                {
                    "bedrooms": 3,
                    "bathrooms": 2.5,
                    "sqft_living": 2000,
                    "sqft_lot": 5000,
                    "floors": 2,
                    "sqft_above": 1500,
                    "sqft_basement": 500,
                    "zipcode": "98125"
                }
            ]
        }
    """
    try:
        # Convert pydantic models to dicts
        records = [r.dict(exclude_none=True) for r in request.instances]
        return predict_prices(records)
    except ValueError as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error during prediction")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/explain/permutation")
def explain_permutation(request: PredictRequest, n_repeats: int = 10):
    """
    Compute permutation importance for the model using given instances.
    Note: can be slow for large input or complex models.
    """
    try:
        records = [r.dict(exclude_none=True) for r in request.instances]
        return explain_permutation_importance(records, n_repeats)
    except ValueError as e:
        logger.error(f"Explanation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error computing permutation importance")
        raise HTTPException(status_code=500, detail="Could not compute importances")
