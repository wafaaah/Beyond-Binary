# DengueWatch: System Architecture

## 1. Overview

DengueWatch is a Streamlit application with a local Python decision engine. It forecasts ward-level dengue cases and plans the response. It has no backend server, database or runtime external API.

## 2. Data Flow

```text
data/raw/dengue_dataset_onsite.csv
              |
   ml/weather_features.py      lagged weather, season, ward features
              |
   models/*.joblib             2, 3 and 4 week forecasts
              |
   ml/allocation.py            risk, demand, constrained allocation
       |             |                    |
 ml/routing.py   ml/dispatch.py     ml/simulator.py
 ml/referral.py  SMS, WhatsApp,     what-if crews
 bed transfers   HTML brief         and ranking
       |             |                    |
              dashboard/ (Streamlit pages)
```

The main Dashboard page also reads `data/raw/dengue_dataset.csv` for historical charts.

## 3. Forecasting

- Model: `HistGradientBoostingRegressor`, Poisson loss, one per horizon.
- Settings: learning rate 0.05, 300 iterations, 15 leaf nodes, 20 samples per leaf, L2 1.0, random state 42.
- 27 features: rainfall lags 2 to 8 weeks; mean, minimum and maximum temperature and humidity lags 2 to 4 weeks; rainfall sums over 2, 4 and 6 weeks; week of year as sine and cosine; population density, water logging risk and sanitation score.
- Features are built per ward in date order. Weather inputs are at least 2 weeks old.
- Chronological split by target date: training to 31 December 2022, validation to 30 June 2024, testing from 1 July 2024.
- Fallback: if the model cannot run, saved predictions in `data/processed/weather_model_predictions.csv` are used and labelled.

## 4. Allocation (`ml/allocation.py`)

1. Demand = predicted cases x factor (saline 2.385, diagnostic kits 1.165, beds 0.298).
2. Priority = risk level, then population density, then predicted cases.
3. Each city pool holds a chosen percentage of its demand and is filled in priority order.
4. Crews form one pool: first one crew per ward in need, then top-ups in priority order.
5. Unmet need is shown as a deficit alert. Allocation never exceeds stock.

## 5. Overflow Routing (`ml/routing.py`, `ml/referral.py`)

- Estimated capacity = 90th percentile of past weekly bed demand x scenario multiplier.
- Overflow moves one patient at a time to the least occupied ward in the same city that has room. Patients who cannot be placed are reported.
- The transfer desk offers the nearest ward with a free bed. Without a `data/ward_locations.csv` file, positions are a schematic grid.

## 6. What-If Simulator (`ml/simulator.py`)

Crews reduce water logging risk and the sanitation gap (25% of the remainder per crew, an assumption). The models predict again for 2, 3 and 4 weeks. A treated ward is never shown worse than its baseline, and untreated wards keep the baseline. Wards are ranked by cases prevented per crew. This is a model counterfactual, not a causal estimate.

## 7. Dispatch (`ml/dispatch.py`)

Fixed templates create team IDs, SMS and WhatsApp text and a printable HTML brief. The user reviews and sends them outside the app.

## 8. Interface

| Part | Files |
|---|---|
| Pages | `Dashboard.py`, `pages/` |
| Scenario controls | `shared.py` |
| Intro and menu | `splash.py`, `nav.py` |
| Demo role sign-in | `role_gate.py` |
| English and Bangla | `i18n.py`, `i18n_pages.py`, `public_en.py` |
| Maps | `command_map.py`, `ops_map.py`, `map3d.py` |
| Public helper | `copilot_engine.py` (keyword matching, no generative model) |

## 9. State, Security and Privacy

- Role, language, scenario, requests and bed updates are kept in the browser session only.
- Sign-in uses fixed demo accounts stored in the code and shown on screen. It is not production security.
- Data is aggregated by ward. No patient records are used.

## 10. Offline Resilience and Performance

Data, models, translations and message templates are local, so a local run does not depend on external services. Streamlit caching reuses loaded data and forecasts. The cloud deployment itself needs internet access.

## 11. Limitations and Next Steps

Limitations: historical replay; assumed capacity, crews and effects; schematic geography; weaker accuracy in high-case weeks.

Next steps: live case and weather feeds, real capacity, stock and location data, case-history features, a database with secure accounts, an SMS gateway and field validation.
