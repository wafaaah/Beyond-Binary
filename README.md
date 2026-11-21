# Beyond-Binary

## DengueWatch — AI-Based Urban Dengue Risk Prediction

DengueWatch is a machine-learning-based project designed to analyze weather-related factors and historical dengue case data to estimate dengue risk across different city wards in Bangladesh.

The system provides ward-level predictions, risk classifications, historical model backtesting, and an interactive dashboard to support data-driven public health awareness and planning.

## Key Features

- Ward-level dengue risk prediction.
- Multi-week forecasting for 2, 3, and 4 weeks.
- Weather-related feature analysis, including temperature, rainfall, and humidity.
- Historical prediction and backtesting.
- Four risk categories: Low, Medium, High, and Critical.
- Interactive Streamlit dashboard.
- Ward and city-based filtering.
- Historical risk distribution and prediction tables.

## Technologies Used

- Python
- Pandas and NumPy
- Scikit-learn
- Joblib
- Streamlit
- Plotly
- Git and GitHub

## Project Structure

```text
Beyond-Binary/
│
├── dashboard/
│   ├── app.py
│   ├── components.py
│   ├── mock_data.py
│   ├── style.py
│   └── action_recommendations.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── ml/
│   ├── weather_features.py
│   ├── train_weather_model.py
│   ├── predict_api_weather.py
│   └── predict_historical_weather.py
│
├── models/
│
├── requirements.txt
├── README.md
└── ARCHITECTURE.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/wafaaah/Beyond-Binary.git
cd Beyond-Binary
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Run the Dashboard

From the project root directory, run:

```bash
streamlit run dashboard/app.py
```

The dashboard will open in your browser.

## Machine Learning Workflow

1. Load historical dengue and weather-related data.
2. Process and prepare the input features.
3. Generate ward-level weather features and multi-week lag variables.
4. Train forecasting models using chronological data splitting.
5. Generate predictions for multiple forecasting horizons.
6. Classify predictions into dengue risk categories.
7. Display results through the interactive dashboard.

## Risk Classification

The model output is classified into four risk levels:

| Risk Level | Predicted Cases |
|---|---:|
| Low | Less than 1 |
| Medium | 1 to less than 5 |
| High | 5 to less than 10 |
| Critical | 10 or more |

## Important Note

The forecasts are experimental model estimates and are not clinically validated. They should not be treated as official dengue outbreak warnings.

Historical backtesting results represent past evaluation periods, not live predictions.

The latest historical input used by the current historical prediction pipeline is dated December 29, 2025.

## AI Assistance and External Resources Disclosure

AI assistance was used during development for coding support, debugging, documentation, and implementation guidance. The team reviewed and tested the project components.

Weather API integration and external data sources should be disclosed here with their actual provider names and usage details.

## Team

**Team Name:** Beyond-Binary

**Project:** DengueWatch

**Hackathon:** EDU AI Engineering Hackathon 2026

**Team Members:** Add all team members' names here.

---

