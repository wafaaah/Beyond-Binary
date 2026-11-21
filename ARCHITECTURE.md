# DengueWatch - System Architecture

## 1. Project Overview

DengueWatch is a machine-learning-based system designed to estimate dengue risk across different city wards using historical dengue cases, weather conditions, and ward-level environmental information.

The system generates 2-week, 3-week, and 4-week predictions and displays ward-level risk classifications through an interactive Streamlit dashboard.

## 2. System Architecture and Data Flow

The system follows this workflow:

```text
Historical Dengue and Weather Dataset
                 |
                 v
        Data Preprocessing
                 |
                 v
       Feature Engineering
                 |
                 v
       Ward-Level Weather Lags
                 |
                 v
       Chronological Data Split
                 |
                 v
       ML Model Training
                 |
                 v
      Three Horizon Models
       (2, 3 and 4 Weeks)
                 |
                 v
       Serialized Joblib Models
                 |
                 v
        Prediction Pipeline
                 |
                 v
       Forecast CSV Files
                 |
                 v
       Streamlit Dashboard
                 |
                 v
      Ward-Level Risk Display
```

## 3. Data Processing and Feature Engineering

The system uses historical dengue and weather records containing rainfall, temperature, humidity, ward information, and environmental indicators.

Data is sorted by ward and date before feature generation to preserve the chronological order of observations.

The feature engineering pipeline generates:

- Rainfall lag features from 2 to 8 weeks.
- Average, minimum, and maximum temperature lags for 2, 3, and 4 weeks.
- Relative humidity lags for 2, 3, and 4 weeks.
- Rolling rainfall sums over 2, 4, and 6 weeks.
- Seasonal features using sine and cosine encoding of the week of the year.
- Ward-level features including population density, waterlogging risk, and sanitation score.

Ward-specific grouping ensures that historical weather features are calculated separately for each ward.

## 4. Machine Learning Model

The project uses `HistGradientBoostingRegressor` with Poisson loss to predict non-negative dengue case counts.

Three separate models are trained for:

- 2-week-ahead prediction.
- 3-week-ahead prediction.
- 4-week-ahead prediction.

The main model configuration includes:

- Learning rate: 0.05
- Maximum iterations: 300
- Maximum leaf nodes: 15
- Minimum samples per leaf: 20
- L2 regularization: 1.0
- Random state: 42

Poisson loss is selected because dengue case counts are non-negative count data.

## 5. Chronological Validation Strategy

To prevent future information from leaking into model training, the dataset is divided chronologically according to the target date.

- Training: Target dates up to December 31, 2022.
- Validation: Target dates after December 31, 2022 and before July 1, 2024.
- Testing: Target dates from July 1, 2024 onward.

This approach evaluates model performance on later periods that were not used during training.

Model performance is measured using:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- R² Score
- High-case MAE for observations with at least 10 dengue cases

## 6. Model Serialization and Prediction

Each trained model is saved using Joblib to avoid retraining whenever predictions are required.

The saved model package contains the trained estimator, feature list, prediction horizon, risk cutoffs, and high-case threshold.

The project uses separate prediction scripts for historical and weather-based forecast generation. The dashboard currently reads its forecast input from `data/processed/api_weather_forecasts.csv`.

This CSV is a pre-generated input file; the dashboard does not need to make a live weather API request when loading it.

## 7. Risk Classification

Predicted dengue case values are converted into four risk categories:

| Risk Level | Predicted Cases |
|---|---:|
| Low | Below 1 |
| Medium | 1 to below 5 |
| High | 5 to below 10 |
| Critical | 10 or above |

These categories help users understand relative dengue risk across wards and forecast periods.

## 8. Dashboard and Efficiency

The interactive dashboard is developed using Streamlit.

It provides:

- City and ward selection.
- Historical dengue case summaries.
- Weather information and historical trends.
- Multi-week forecast information.
- Ward-level risk classification.
- Historical prediction and backtesting information.
- Action recommendations.

The dashboard uses Streamlit caching with `@st.cache_data` to reduce repeated CSV loading and processing.

Serialized Joblib models reduce unnecessary model retraining. Pre-generated forecast CSV files also reduce repeated prediction computation during dashboard usage.

## 9. Limitations

Predictions depend on the quality and coverage of the available historical dataset. Weather-related patterns do not guarantee future dengue outbreaks.

The system is designed as a decision-support and awareness tool, not as a replacement for official public health surveillance or medical advice.

Predictions should be interpreted with appropriate caution and require further validation before real-world public health deployment.