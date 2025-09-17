import pathlib

# Paths
BASE_DIR = pathlib.Path(__file__).parent.parent.parent
MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "model.pkl"
FEATURES_PATH = MODEL_DIR / "model_features.json"
DEMOGRAPHICS_PATH = BASE_DIR / "data" / "zipcode_demographics.csv"

# Model configuration
IMPUTE_STRATEGY = {}

# API Configuration
APP_TITLE = "[PhData] - House Price Predictor MVP"
