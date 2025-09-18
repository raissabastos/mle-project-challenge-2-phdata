# House Price Prediction API - ReadMe

## Folder Structure

```
mle-project-challenge-2/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # Centralized settings
│   ├── services/
│   │   ├── __init__.py
│   │   └── predictor.py         # Prediction functions
│   └── utils/
│       ├── __init__.py
│       └── logger.py            # Logging config
├── routes/
│   ├── __init__.py
│   ├── health.py               # Health check routes
│   └── predict.py              # Prediction routes
├── interfaces/
│   ├── __init__.py
│   └── schemas.py              # Validation schemas (Pydantic models)
├── tests/
│   ├── __init__.py
│   ├── test_script_detail.py         # Test with explanation
│   ├── test_script.py          # Simple test
│   └── evaluate_model.py       # Model evaluation
├── data/                         # Data
├── model/                        # Trained models
├── create_model.py              # Training script
├── main.py
└── requirements.txt
```

### Basic Docker Run
```bash
# Build the image
docker build -t house-predictor .

# Run container
docker run -p 8000:8000 -v ./model:/app/model -v ./data:/app/data house-predictor

# See container logs
docker logs -f <container_id> 

# See realtime logs
docker logs -f house-predictor
```

<!-- ### With Nginx

- reverse proxy:

```bash
# 1. Run the application
docker run -d --name house-predictor -p 8000:8000 \
  -v ./model:/app/model \
  -v ./data:/app/data \
  house-predictor

# 2. Run Nginx
docker run -d --name nginx -p 80:80 \
  -v ./nginx.conf:/etc/nginx/nginx.conf:ro \
  --link house-predictor:house-predictor \
  nginx:alpine
``` -->

The API will be available at: `http://0.0.0.0:8000`

## Documentation
- **Swagger UI**: `http://0.0.0.0:8000/docs`

## Data Format

### Required Features
- `bedrooms`: Number of bedrooms (int ≥ 0)
- `bathrooms`: Number of bathrooms (float ≥ 0)
- `sqft_living`: Living area in square feet (int > 0)
- `sqft_lot`: Lot area in square feet (int > 0)
- `floors`: Number of floors (float ≥ 0)
- `sqft_above`: Area above ground (int ≥ 0)
- `sqft_basement`: Basement area (int ≥ 0)

### Optional Features
- `zipcode`: Zip code (string) — **recommended** for better accuracy
- `waterfront`: Waterfront view (0 or 1)
- `view`: View quality (0-4)
- `condition`: House condition (1-5)
- `grade`: Overall house grade (1-13)
- `yr_built`: Year built (1800-2024)
- `yr_renovated`: Year renovated [0: Never renovated] (0-2024)
- `lat`: Latitude (-90 to 90)
- `long`: Longitude (-180 to 180)
- `sqft_living15`: Living area of 15 nearest neighbors
- `sqft_lot15`: Lot area of 15 nearest neighbors

## Available Endpoints

### 1. Health Check
**GET** `/health`

Check if API and model are working fine.

**Response:**
```json
{
    "status": "ok",
    "model_loaded": true,
    "model_version": "1.0"
}
```

### 2. Model Metadata
**GET** `/metadata`

Return detailed info about the loaded model.

**Response:**
```json
{
    "model_loaded": true,
    "model_version": "1.0",
    "n_features": 33
}
```

### 3. Price Prediction
**POST** `/predict`

Predict price for one or more houses.

**Minimum Payload:**
```json
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
```

**Response:**
```json
{
    "predictions": [
        {
            "prediction": "$450000.0",
            "input_index": 0,
            "confidence": 0.85
        }
    ],
    "model_version": "1.0",
    "n_predictions": 1,
    "latency_seconds": 0.123,
    "request_id": "123e4567-e89b-12d3-a456-426614174000",
    "timestamp": 1640995200
}
```

### 4. Model Explanation
**POST** `/explain/permutation`

Calculate feature importance for the given predictions.

**Payload:** Same format as `/predict`

**Parameters:**
- `n_repeats` (query): Number of repeats for calculation (default: 10)

**Response:**
```json
{
    "importances": [
        ["sqft_living", 0.25],
        ["grade", 0.18],
        ["sqft_above", 0.15],
        ["bathrooms", 0.12],
        ["bedrooms", 0.10]
    ]
}
```
