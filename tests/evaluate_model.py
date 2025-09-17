# evaluate_model.py
import pathlib
import pickle
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.inspection import permutation_importance

BASE = pathlib.Path(__file__).parent.parent
MODEL_PATH = BASE / "model" / "model.pkl"
FEATURES_PATH = BASE / "model" / "model_features.json"
DATA_PATH = BASE / "data" / "kc_house_data.csv"  # dataset with price

def load_model():
    with open(MODEL_PATH, "rb") as f:
        m = pickle.load(f)
    return m

def load_features():
    try:
        with open(FEATURES_PATH, "r") as f:
            return json.load(f)
    except:
        return None

def load_data():
    df = pd.read_csv(DATA_PATH, dtype={"zipcode": str})
    # Ensure price exists
    if "price" not in df.columns:
        raise RuntimeError("price column not found in dataset")
    y = df["price"]
    X = df.drop(columns=["price"])
    return X, y

def align_features(X, model_features):
    X = X.copy()

    if "zipcode" in X.columns and model_features and "zipcode" not in model_features:
        X = X.drop(columns=["zipcode"])
    if model_features:
        for c in model_features:
            if c not in X.columns:
                X[c] = 0
        X = X[model_features]
    X = X.fillna(0)
    return X

def main(test_size=0.2, random_state=42):
    model = load_model()
    model_features = load_features()
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    X_test_aligned = align_features(X_test, model_features)

    preds = model.predict(X_test_aligned)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    print("Evaluation results:")
    print(f"  RMSE: {rmse:.2f}")
    print(f"  MAE : {mae:.2f}")
    print(f"  R2  : {r2:.4f}")

    # Feature importance if available
    if hasattr(model, "feature_importances_"):
        importances = getattr(model, "feature_importances_")
        feat_names = model_features if model_features else X_test_aligned.columns.tolist()
        top = sorted(zip(feat_names, importances), key=lambda x: x[1], reverse=True)[:20]
        print("\nTop feature importances (model.feature_importances_):")
        for f, v in top:
            print(f"  {f}: {v:.6f}")
    else:
        # permutation importance
        try:
            print("\nComputing permutation importance (this may take a while)...")
            r = permutation_importance(model, X_test_aligned, preds, n_repeats=10, random_state=0)
            feat_names = model_features if model_features else X_test_aligned.columns.tolist()
            top = sorted(zip(feat_names, r.importances_mean), key=lambda x: abs(x[1]), reverse=True)[:20]
            print("Top permutation importances:")
            for f, v in top:
                print(f"  {f}: {v:.6f}")
        except Exception as e:
            print("Could not compute permutation importance:", e)

if __name__ == "__main__":
    main()
