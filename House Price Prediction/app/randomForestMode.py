import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from scipy.sparse import issparse
from sklearn.impute import SimpleImputer
import joblib


current_dir = os.path.dirname(os.path.abspath(__file__))
projects_dir = os.path.dirname(os.path.dirname(current_dir))

data_dir = os.path.join(projects_dir, "data", "House Price Prediction")
cleaned_file = os.path.join(data_dir, "train_cleaned.csv")

model_dir = os.path.join(current_dir, "models")
os.makedirs(model_dir, exist_ok=True)



df = pd.read_csv(cleaned_file)

y = df["Price_Log"]
X = df.drop(columns=["Price_INR_Lakhs", "Price_Log"])  # leakage se bachne ke liye

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

cat_cols = ["City", "Locality_Type", "Property_Type", "Furnishing_Status"]
binary_cols = ["Parking", "Lift_Available", "Gated_Community"]
num_cols = [
    "BHK", "Bathrooms", "Super_Area_SqFt", "Carpet_Area_SqFt",
    "Floor_Number", "Total_Floors", "Age_of_Property",
    "Distance_to_Metro_km", "Distance_to_City_Center_km",
]

# preprocessor = ColumnTransformer(
#     transformers=[
#         ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), cat_cols),
#         ("num", StandardScaler(), num_cols),
#         ("bin", "passthrough", binary_cols),
#     ]
# )

feature_cols = cat_cols + num_cols + binary_cols

# Categorical preprocessing
cat_preprocessor = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

# Numerical preprocessing
num_preprocessor = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median"))
])

# Binary preprocessing
bin_preprocessor = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent"))
])

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", cat_preprocessor, cat_cols),
        ("num", num_preprocessor, num_cols),
        ("bin", bin_preprocessor, binary_cols)
    ],
    remainder="drop"
)

# print(X[feature_cols].isnull().sum())



rf_model = Pipeline(steps=[
    ("preprocess", preprocessor),

    ("regressor", RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features=1.0,
        random_state=42,
        n_jobs=-1
    ))
])
rf_model.fit(X_train, y_train)

print("Random Forest training completed!")

def evaluate_rf(y_true_log, y_pred_log):

    actual = np.expm1(y_true_log)
    predicted = np.expm1(y_pred_log)

    mae = mean_absolute_error(actual, predicted)

    mse = mean_squared_error(actual, predicted)

    rmse = np.sqrt(mse)

    r2 = r2_score(actual, predicted)

    return {
        "MAE": round(mae, 2),
        "MSE": round(mse, 2),
        "RMSE": round(rmse, 2),
        "R2": round(r2, 4)
    }


train_pred_log = rf_model.predict(X_train)

test_pred_log = rf_model.predict(X_test)

train_metrics = evaluate_rf(y_train, train_pred_log)

test_metrics = evaluate_rf(y_test, test_pred_log)

joblib.dump(
    rf_model,
    "app/models/random_forest_pipeline.joblib"
)

print("\n===== RANDOM FOREST COMPARISON =====")

print("\nTraining Performance:")
for metric, value in train_metrics.items():
    print(f"{metric}: {value}")

print("\nTesting Performance:")
for metric, value in test_metrics.items():
    print(f"{metric}: {value}")