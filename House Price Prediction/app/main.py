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

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), cat_cols),
        ("num", StandardScaler(), num_cols),
        ("bin", "passthrough", binary_cols),
    ]
)

# linear regression model code 

# model = Pipeline(steps=[
#     ("preprocess", preprocessor),
#     ("regressor", LinearRegression()),
# ])
# model.fit(X_train, y_train)


house = {
    "City": "Delhi",
    "Locality_Type": "Mid-Range",
    "Property_Type": "Apartment",
    "BHK": 3,
    "Bathrooms": 2,
    "Super_Area_SqFt": 1000.0,
    "Carpet_Area_SqFt": 800.0,      # fixed: carpet < super
    "Floor_Number": 5,
    "Total_Floors": 12,
    "Age_of_Property": 5,
    "Furnishing_Status": "Semi-Furnished",
    "Parking": 1,
    "Lift_Available": 0,
    "Gated_Community": 1,
    "Distance_to_Metro_km": 2.0,
    "Distance_to_City_Center_km": 9.0,
}


# assert house["Carpet_Area_SqFt"] <= house["Super_Area_SqFt"], "Carpet > Super"
# assert house["Floor_Number"] <= house["Total_Floors"], "Floor > Total floors"
# for col in ["City", "Locality_Type", "Property_Type", "Furnishing_Status"]:
#     assert house[col] in set(X_train[col]), f"Unknown {col}: {house[col]}"


# house_df = pd.DataFrame([house])[X_train.columns]

# pre = model.named_steps["preprocess"]
# reg = model.named_steps["regressor"]

# X_enc = pre.transform(house_df)
# X_enc = X_enc.toarray() if issparse(X_enc) else X_enc
# names = pre.get_feature_names_out()


# scaler = pre.named_transformers_["num"]
# i = num_cols.index("Super_Area_SqFt")
# z_manual = (house["Super_Area_SqFt"] - scaler.mean_[i]) / scaler.scale_[i]
# # print(f"Super_Area: mean={scaler.mean_[i]:.1f}, std={scaler.scale_[i]:.1f}, z={z_manual:.3f}")


# trace = pd.DataFrame({
#     "feature": names,
#     "value": X_enc[0],
#     "coef": reg.coef_,
# })
# trace["contribution"] = trace["value"] * trace["coef"]


# pred_log_manual = reg.intercept_ + trace["contribution"].sum()
# pred_log_model = model.predict(house_df)[0]

# # y_pred = model.predict(X_test)
# y_pred_log = model.predict(X_test)

# # Convert both values into original price scale
# y_test_actual = np.expm1(y_test)
# y_pred_actual = np.expm1(y_pred_log)

# assert np.isclose(pred_log_manual, pred_log_model)   # dono same aane chahiye

# pred_lakhs = np.expm1(pred_log_model)
# print(f"\nFinal price: {pred_lakhs:.2f} Lakhs (~Rs {pred_lakhs/100:.2f} Crore)")  


# # Calculate metrics
# mae = mean_absolute_error(y_test_actual, y_pred_actual)

# mse = mean_squared_error(y_test_actual, y_pred_actual)

# rmse = np.sqrt(mse)


# comparison = pd.DataFrame({
#     "Actual_Price": y_test_actual,
#     "Predicted_Price": y_pred_actual
# })

# comparison["Error"] = (
#     comparison["Actual_Price"] -
#     comparison["Predicted_Price"]
# )

# comparison["Absolute_Error"] = (
#     comparison["Error"].abs()
# )

# worst_predictions = comparison.sort_values(
#     by="Absolute_Error",
#     ascending=False
# ).head(20)

# print("\n===== 20 Worst Predictions =====")
# print(worst_predictions.round(2))


# worst_houses = X_test.loc[worst_predictions.index]

# worst_analysis = pd.concat(
#     [worst_houses, worst_predictions],
#     axis=1
# )

# print(worst_analysis.to_string())

# print("\n===== Model Evaluation =====")
# print(f"MAE:  {mae:.2f} Lakhs")
# print(f"MSE:  {mse:.2f} Lakhs²")
# print(f"RMSE: {rmse:.2f} Lakhs")


# ---------------------------------------------------------------
# 10. SAVE MODEL
# ---------------------------------------------------------------
# model_path = os.path.join(model_dir, "linear_regression.joblib")
# joblib.dump(model, model_path)
# print(f"\nModel saved: {model_path}")


# regression model train. =========================>>>>> regression model =============>>>>>
# dt_model = Pipeline(steps=[
#     ("preprocess", preprocessor),

#     ("regressor", DecisionTreeRegressor(
#         criterion="squared_error",
#         max_depth=15,
#         min_samples_split=10,
#         min_samples_leaf=5,
#         random_state=42
#     ))
# ])

# dt_model.fit(X_train, y_train)

# print("Decision Tree training completed!")
# y_pred_log = dt_model.predict(X_test)
# y_test_actual = np.expm1(y_test)

# y_pred_actual = np.expm1(y_pred_log)

# mae = mean_absolute_error(
#     y_test_actual,
#     y_pred_actual
# )

# mse = mean_squared_error(
#     y_test_actual,
#     y_pred_actual
# )

# rmse = np.sqrt(mse)

# r2 = r2_score(
#     y_test_actual,
#     y_pred_actual
# )

# print("\n===== Decision Tree Evaluation =====")
# print(f"MAE:  {mae:.2f} Lakhs")
# print(f"MSE:  {mse:.2f} Lakhs²")
# print(f"RMSE: {rmse:.2f} Lakhs")
# print(f"R2:   {r2:.4f}")


# # Training predictions
# train_pred_log = dt_model.predict(X_train)

# # Convert to original price scale
# train_actual = np.expm1(y_train)
# train_pred_actual = np.expm1(train_pred_log)

# # Training MAE
# train_mae = mean_absolute_error(
#     train_actual,
#     train_pred_actual
# )

# # Testing MAE
# test_mae = mean_absolute_error(
#     y_test_actual,
#     y_pred_actual
# )

# print("\n===== Training vs Testing =====")

# print(f"Training MAE: {train_mae:.2f} Lakhs")
# print(f"Testing MAE:  {test_mae:.2f} Lakhs")

# =============================== rendom forest model =======================
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

# Train model
rf_model.fit(X_train, y_train)

print("Random Forest training completed!")
y_pred_log = rf_model.predict(X_test)

# Convert predictions to original price scale
y_pred_actual = np.expm1(y_pred_log)

# Convert actual test values to original price scale
y_test_actual = np.expm1(y_test)
mae = mean_absolute_error(y_test_actual, y_pred_actual)

mse = mean_squared_error(y_test_actual, y_pred_actual)

rmse = np.sqrt(mse)

r2 = r2_score(y_test_actual, y_pred_actual)

print("\n===== Random Forest Evaluation =====")

print(f"MAE:  {mae:.2f} Lakhs")
print(f"MSE:  {mse:.2f} Lakhs²")
print(f"RMSE: {rmse:.2f} Lakhs")
print(f"R2:   {r2:.4f}")

# Training predictions
train_pred_log = rf_model.predict(X_train)

# Convert to original price scale
train_actual = np.expm1(y_train)
train_pred_actual = np.expm1(train_pred_log)

# Calculate MAE
train_mae = mean_absolute_error(
    train_actual,
    train_pred_actual
)

test_mae = mean_absolute_error(
    y_test_actual,
    y_pred_actual
)

print("\n===== Training vs Testing =====")

print(f"Training MAE: {train_mae:.2f} Lakhs")
print(f"Testing MAE:  {test_mae:.2f} Lakhs")


feature_names = (
    rf_model
    .named_steps["preprocess"]
    .get_feature_names_out()
)

importances = (
    rf_model
    .named_steps["regressor"]
    .feature_importances_
)

importance_df = pd.DataFrame({
    "Feature": feature_names,
    "Importance": importances
})

importance_df = importance_df.sort_values(
    by="Importance",
    ascending=False
)

print("\n===== Random Forest Feature Importance =====")

print(importance_df.head(20).round(4).to_string(index=False))