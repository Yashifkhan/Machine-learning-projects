
import { useState } from "react";

const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1/predict/house-price";

const initialHouse = {
  City: "Delhi",
  Locality_Type: "Mid-Range",
  Property_Type: "Apartment",
  BHK: 3,
  Bathrooms: 2,
  Super_Area_SqFt: 1000,
  Carpet_Area_SqFt: 800,
  Floor_Number: 5,
  Total_Floors: 12,
  Age_of_Property: 5,
  Furnishing_Status: "Semi-Furnished",
  Parking: 1,
  Lift_Available: 0,
  Gated_Community: 1,
  Distance_to_Metro_km: 2,
  Distance_to_City_Center_km: 9,
};

const dropdownOptions = {
  City: [
    "Chandigarh",
    "Kolkata",
    "Delhi",
    "Ahmedabad",
    "Pune",
    "Hyderabad",
    "Mumbai",
    "Bangalore",
    "Jaipur",
    "Chennai",
  ],
  Locality_Type: ["Mid-Range", "Premium", "Affordable"],
  Property_Type: [
    "Builder Floor",
    "Villa",
    "Apartment",
    "Independent House",
  ],
  Furnishing_Status: [
    "Semi-Furnished",
    "Unfurnished",
    "Furnished",
  ],
};

const numericFields = [
  { key: "BHK", label: "Bedrooms (BHK)", min: 1, max: 6 },
  { key: "Bathrooms", label: "Bathrooms", min: 1, max: 6 },
  {
    key: "Super_Area_SqFt",
    label: "Super Area (Sq Ft)",
    min: 1,
    step: 0.01,
  },
  {
    key: "Carpet_Area_SqFt",
    label: "Carpet Area (Sq Ft)",
    min: 1,
    step: 0.01,
  },
  { key: "Floor_Number", label: "Floor Number", min: 0, max: 44 },
  { key: "Total_Floors", label: "Total Floors", min: 1, max: 44 },
  {
    key: "Age_of_Property",
    label: "Property Age (Years)",
    min: 0,
    max: 40,
  },
  {
    key: "Distance_to_Metro_km",
    label: "Distance to Metro (KM)",
    min: 0,
    step: 0.01,
  },
  {
    key: "Distance_to_City_Center_km",
    label: "Distance to City Center (KM)",
    min: 0,
    step: 0.01,
  },
];

const binaryFields = [
  { key: "Parking", label: "Parking Available" },
  { key: "Lift_Available", label: "Lift Available" },
  { key: "Gated_Community", label: "Gated Community" },
];

const inputClass =
  "w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100";

const labelClass =
  "mb-2 block text-xs font-semibold text-slate-600";

function App() {
  const [house, setHouse] = useState(initialHouse);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (key, value) => {
    setHouse((prev) => ({
      ...prev,
      [key]: value,
    }));

    setPrediction(null);
    setError("");
  };

  const renderDropdown = (key, label, options) => (
    <div key={key}>
      <label htmlFor={key} className={labelClass}>
        {label}
      </label>

      <select
        id={key}
        className={inputClass}
        value={house[key]}
        onChange={(e) => handleChange(key, e.target.value)}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );

  const renderNumberInput = (field) => (
    <div key={field.key}>
      <label htmlFor={field.key} className={labelClass}>
        {field.label}
      </label>

      <input
        id={field.key}
        type="number"
        className={inputClass}
        min={field.min}
        max={field.max}
        step={field.step || 1}
        required
        value={house[field.key]}
        onChange={(e) =>
          handleChange(
            field.key,
            e.target.value === "" ? "" : Number(e.target.value)
          )
        }
      />
    </div>
  );

  const renderBinaryDropdown = (field) => (
    <div key={field.key}>
      <label htmlFor={field.key} className={labelClass}>
        {field.label}
      </label>

      <select
        id={field.key}
        className={inputClass}
        value={house[field.key]}
        onChange={(e) =>
          handleChange(field.key, Number(e.target.value))
        }
      >
        <option value={1}>Yes</option>
        <option value={0}>No</option>
      </select>
    </div>
  );

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setPrediction(null);

    if (house.Carpet_Area_SqFt > house.Super_Area_SqFt) {
      setError("Carpet area cannot exceed super area.");
      return;
    }

    if (house.Floor_Number > house.Total_Floors) {
      setError("Floor number cannot exceed total floors.");
      return;
    }

    const emptyField = Object.values(house).some(
      (value) => value === "" || value === null || !Number.isFinite(
        typeof value === "number" ? value : 1
      )
    );

    if (emptyField) {
      setError("Please fill in all property details.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
       body: JSON.stringify({
        features: house,
      }),
      });

      const data = await response.json();
      console.log("API Response:", data);

      if (!response.ok) {
        throw new Error(
          data.detail || data.error || "Prediction failed."
        );
      }

      const result =
        data.predicted_price_in_lakhs ??
        data.prediction ??
        data.price;

        console.log(result);
      if (result === undefined || result === null) {
        throw new Error("Prediction value missing in API response.");
      }

      const price = Number(result);

      if (!Number.isFinite(price)) {
        throw new Error("Backend returned an invalid price.");
      }

      setPrediction(price);
    } catch (err) {
      setError(err.message || "Unable to connect to backend.");
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setHouse({ ...initialHouse });
    setPrediction(null);
    setError("");
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">

      {/* Header */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">

          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-900 text-xl font-bold text-white">
              H
            </div>

            <div>
              <h2 className="text-lg font-extrabold tracking-tight">
                HomeValue
              </h2>
              <p className="text-[9px] font-semibold tracking-[2px] text-slate-400">
                PROPERTY INTELLIGENCE
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-full bg-green-50 px-3 py-2 text-xs font-semibold text-green-700">
            <span className="h-2 w-2 rounded-full bg-green-500" />
            Random Forest Model
          </div>

        </div>
      </header>

      {/* Hero */}
      <section className="px-5 pb-10 pt-14 text-center">
        <span className="text-[11px] font-bold tracking-[2px] text-blue-700">
          SMART PROPERTY VALUATION
        </span>

        <h1 className="mt-4 text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl lg:text-5xl">
          Discover Your Property's Value
        </h1>

        <p className="mx-auto mt-4 max-w-xl text-sm leading-7 text-slate-500">
          Enter your property details and get an estimated
          market price powered by Machine Learning.
        </p>
      </section>

      {/* Main Content */}
      <main className="mx-auto grid max-w-7xl grid-cols-1 items-start gap-6 px-5 pb-16 lg:grid-cols-[1.7fr_0.9fr] lg:px-8">

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-8"
        >

          <div className="mb-8 flex items-start justify-between gap-3">
            <div>
              <h2 className="text-xl font-bold text-slate-900">
                Property Details
              </h2>
              <p className="mt-2 text-xs text-slate-400">
                Enter all details to estimate your property price.
              </p>
            </div>

            <button
              type="button"
              onClick={resetForm}
              className="rounded-lg border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-100"
            >
              Reset
            </button>
          </div>

          {/* Location */}
          <section className="border-t border-slate-100 py-6">
            <h3 className="mb-5 text-sm font-bold text-blue-900">
              01. Location Information
            </h3>

            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
              {renderDropdown(
                "City",
                "City",
                dropdownOptions.City
              )}

              {renderDropdown(
                "Locality_Type",
                "Locality Type",
                dropdownOptions.Locality_Type
              )}

              {numericFields
                .filter((field) =>
                  [
                    "Distance_to_Metro_km",
                    "Distance_to_City_Center_km",
                  ].includes(field.key)
                )
                .map(renderNumberInput)}
            </div>
          </section>

          {/* Property Information */}
          <section className="border-t border-slate-100 py-6">
            <h3 className="mb-5 text-sm font-bold text-blue-900">
              02. Property Information
            </h3>

            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
              {renderDropdown(
                "Property_Type",
                "Property Type",
                dropdownOptions.Property_Type
              )}

              {renderNumberInput(numericFields[0])}
              {renderNumberInput(numericFields[1])}

              {renderDropdown(
                "Furnishing_Status",
                "Furnishing Status",
                dropdownOptions.Furnishing_Status
              )}

              {numericFields
                .filter((field) =>
                  [
                    "Super_Area_SqFt",
                    "Carpet_Area_SqFt",
                    "Floor_Number",
                    "Total_Floors",
                    "Age_of_Property",
                  ].includes(field.key)
                )
                .map(renderNumberInput)}
            </div>
          </section>

          {/* Amenities */}
          <section className="border-t border-slate-100 py-6">
            <h3 className="mb-5 text-sm font-bold text-blue-900">
              03. Facilities & Amenities
            </h3>

            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
              {binaryFields.map(renderBinaryDropdown)}
            </div>
          </section>

          {/* Error */}
          {error && (
            <div
              role="alert"
              className="mb-5 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600"
            >
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-3 rounded-xl bg-blue-900 px-5 py-4 text-sm font-bold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading
              ? "Calculating Price..."
              : "Predict Property Price"}

            {!loading && <span className="text-lg">→</span>}
          </button>

          <p className="mt-4 text-center text-[11px] text-slate-400">
            All 16 features are sent to the Random Forest model.
          </p>

        </form>

        {/* Prediction Result */}
        <aside className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:sticky lg:top-6">

          <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-2xl font-bold text-blue-800">
            ₹
          </div>

          <span className="text-[10px] font-bold tracking-[2px] text-blue-600">
            PROPERTY VALUATION
          </span>

          <h2 className="mt-2 text-xl font-bold text-slate-900">
            Your Estimated Price
          </h2>

          {prediction !== null ? (
            <div className="mt-9 rounded-xl bg-blue-50 p-6">
              <p className="text-xs font-semibold text-blue-600">
                PREDICTED PROPERTY PRICE
              </p>

              <h3 className="mt-3 break-words text-3xl font-extrabold text-blue-900 sm:text-4xl">
                ₹{prediction.toLocaleString("en-IN", {
                  maximumFractionDigits: 2,
                })}
              </h3>

              <p className="mt-3 text-xs text-blue-700">
                INR Lakhs · Estimated model output
              </p>
            </div>
          ) : (
            <div className="py-12 text-center">
              <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-slate-100 text-4xl text-blue-700">
                ⌂
              </div>

              <h3 className="mt-5 font-bold text-slate-800">
                Waiting for Details
              </h3>

              <p className="mx-auto mt-3 max-w-xs text-xs leading-6 text-slate-400">
                Fill in your property information and click
                Predict Property Price to see your result.
              </p>
            </div>
          )}

          <div className="my-6 border-t border-slate-100" />

          <div className="space-y-5">
            <div>
              <p className="text-xs text-slate-400">
                Prediction Algorithm
              </p>
              <p className="mt-1 text-sm font-bold text-slate-700">
                Random Forest Regressor
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-400">
                Input Features
              </p>
              <p className="mt-1 text-sm font-bold text-slate-700">
                16 Features
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-400">
                Prediction Output
              </p>
              <p className="mt-1 text-sm font-bold text-slate-700">
                INR Lakhs
              </p>
            </div>
          </div>

          <div className="mt-7 rounded-lg bg-slate-50 p-4">
            <p className="text-[11px] leading-6 text-slate-500">
              This prediction is an estimate generated by a
              machine learning model. Actual market prices may vary.
            </p>
          </div>

        </aside>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white px-5 py-6 text-center text-xs text-slate-400">
        HomeValue · Machine Learning Property Prediction
      </footer>

    </div>
  );
}

export default App;
