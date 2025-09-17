import pickle
import json
import time
import uuid
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.inspection import permutation_importance

from ..config.settings import MODEL_PATH, FEATURES_PATH, DEMOGRAPHICS_PATH, IMPUTE_STRATEGY
from ..utils.logger import setup_logger

logger = setup_logger()

# Global resources
model = None
model_features = None
demographics = None
model_version = None


def load_artifacts():
    """Load necessary artifacts (model, features, demographics)"""
    global model, model_features, demographics, model_version
    
    # Load model
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        model_version = getattr(model, "random_state", "1.0.1") or getattr(model, "__class__", type(model)).__name__
        logger.info(f"Loaded model from {MODEL_PATH} (version: {model_version})")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        model = None

    # Load features
    try:
        with open(FEATURES_PATH, "r") as f:
            model_features = json.load(f)
        logger.info(f"Loaded {len(model_features)} model features")
    except Exception as e:
        logger.warning(f"Could not load features list: {e}")
        model_features = None

    # Load demographics
    try:
        demographics = pd.read_csv(DEMOGRAPHICS_PATH, dtype={"zipcode": str})
        logger.info(f"Loaded demographics with {len(demographics)} rows")
    except Exception as e:
        demographics = None
        logger.warning(f"Could not load demographics: {e}")


def prepare_input(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare input data for prediction by merging demographics data"""
    # Ensure copy
    df = df.copy()
    if "zipcode" in df.columns:
        df["zipcode"] = df["zipcode"].astype(str)
        if demographics is not None:
            df = df.merge(demographics, how="left", on="zipcode")
    # drop zipcode
    if "zipcode" in df.columns:
        df = df.drop(columns=["zipcode"])
    # ensure model features order
    if model_features:
        for c in model_features:
            if c not in df.columns:
                df[c] = IMPUTE_STRATEGY.get(c, 0)
        df = df[model_features]
    # final imputation
    df = df.fillna(0)
    return df


def predict_prices(instances: list) -> Dict[str, Any]:
    """Predict house prices"""
    if model is None:
        raise ValueError("Model unavailable")
    
    # Convert instances to DataFrame
    df = pd.DataFrame(instances)
    if df.empty:
        raise ValueError("Empty input")

    start = time.time()
    X = prepare_input(df)
    preds = model.predict(X)

    # Confidence for KNeighborsRegressor
    if hasattr(model[-1], "kneighbors"):
        knn = model[-1]
        distances, neighbor_indices = knn.kneighbors(X, return_distance=True)
        confidences = []
        for dists, inds in zip(distances, neighbor_indices):
            neighbor_values = knn._y[inds]
            weights = 1 / (dists + 1e-6)  # closer = bigger weight
            weighted_mean = np.average(neighbor_values, weights=weights)
            # weighted std = sqrt(Σ w_i * (x_i - mean)^2 / Σ w_i)
            weighted_var = np.average((neighbor_values - weighted_mean) ** 2, weights=weights)
            weighted_std = np.sqrt(weighted_var)
            confidence = 1 - (weighted_std / (weighted_mean + 1e-6))
            confidence = max(0, min(1, confidence))
            confidences.append(confidence)
    else:
        confidences = [None] * len(preds)

    latency = time.time() - start
    results = []
    for i, p in enumerate(preds):
        results.append({
            "prediction": "$" + str(float(p)),
            "input_index": i,
            "confidence": confidences[i]
        })

    return {
        "predictions": results,
        "model_version": str(model_version),
        "n_predictions": len(results),
        "latency_seconds": latency,
        "request_id": str(uuid.uuid4()),
        "timestamp": int(time.time())
    }


def explain_permutation_importance(instances: list, n_repeats: int = 10) -> Dict[str, Any]:
    """Calculates permutation importance using sklearn."""
    if model is None:
        raise ValueError("Model unavailable")
    
    df = pd.DataFrame(instances)
    if df.empty:
        raise ValueError("Empty input")

    X = prepare_input(df)

    r = permutation_importance(model, X, model.predict(X), n_repeats=n_repeats, random_state=0)
    importances = dict(zip(X.columns.tolist(), r.importances_mean.tolist()))
    # top 10
    topk = sorted(importances.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
    return {"importances": topk}



def get_model_status() -> Dict[str, Any]:
    """Returns model status"""
    return {
        "model_loaded": model is not None,
        "model_version": str(model_version),
        "n_features": len(model_features) if model_features else None,
    }
