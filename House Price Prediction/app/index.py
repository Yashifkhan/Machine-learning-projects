
import joblib
import pandas as pd
import numpy as np

from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
from fastapi.middleware.cors import CORSMiddleware


# =====================================
# 1. APP CONFIGURATION
# =====================================

app = FastAPI(
    title="House Price Prediction API",
    description="Random Forest House Price Prediction",
    version="1.0.0"
)


# =====================================
# 2. CORS CONFIGURATION
# =====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================
# 3. LOAD SAVED MODEL
# =====================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "random_forest_pipeline.joblib"

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model file not found: {MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)

print("Random Forest model loaded successfully!")


# =====================================
# 4. GET TRAINING FEATURE COLUMNS
# =====================================

FEATURE_COLUMNS = getattr(model, "feature_names_in_", None)

if FEATURE_COLUMNS is None:
    raise ValueError(
        "Training feature names not found. "
        "Save the complete fitted pipeline with its "
        "original feature columns."
    )

FEATURE_COLUMNS = list(FEATURE_COLUMNS)

print("Model Features:", FEATURE_COLUMNS)


# =====================================
# 5. REQUEST SCHEMA
# =====================================

class HouseFeatures(BaseModel):
    features: dict[str, Any]


# =====================================
# 6. ROOT ROUTE
# =====================================

@app.get("/")
def home():

    return {
        "message": "House Price Prediction API is running",
        "model": "Random Forest",
        "status": "success"
    }


# =====================================
# 7. HEALTH CHECK
# =====================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "model_loaded": model is not None
    }


# =====================================
# 8. MODEL INFORMATION
# =====================================

@app.get("/api/v1/model-info")
def model_info():

    return {
        "model": "Random Forest",
        "features": FEATURE_COLUMNS,
        "total_features": len(FEATURE_COLUMNS),
        "target": "Price_INR_Lakhs"
    }


# =====================================
# 9. PREDICTION API
# =====================================

@app.post("/api/v1/predict/house-price")
def predict_house_price(data: HouseFeatures):

    try:

        input_data = data.features

        # Check missing features
        missing_features = [
            col for col in FEATURE_COLUMNS
            if col not in input_data
        ]

        if missing_features:

            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Missing required features",
                    "missing_features": missing_features
                }
            )

        # Create DataFrame in original training order
        input_df = pd.DataFrame(
            [[input_data[col] for col in FEATURE_COLUMNS]],
            columns=FEATURE_COLUMNS
        )

        # Predict using saved pipeline
        prediction_log = model.predict(input_df)[0]

        # Convert log1p prediction to original price
        predicted_price = np.expm1(prediction_log)

        return {
            "status": "success",
            "model": "Random Forest",
            "predicted_price_in_lakhs": round(
                float(predicted_price), 2
            ),
            "currency": "INR",
            "unit": "Lakhs"
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
