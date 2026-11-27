# Beyond-Binary

## DengueWatch: Urban Dengue Forecast and Response Dashboard

**Live app:** https://beyondbinary-denguewatch.streamlit.app/

DengueWatch forecasts ward-level dengue risk 2 to 4 weeks ahead for 60 wards in 5 city corporations of Bangladesh, and turns the forecast into actions: supply and crew allocation, hospital overflow routing, what-if vector control and dispatch messages.

The app shows a **historical replay**, not live surveillance.

## Users and Demo Accounts

| Role | Username | Password | Main work |
|---|---|---|---|
| Ward Health Officer | `officer` | `officer123` | Ward risk, supply and spray requests, field SMS |
| Hospital Manager | `hospital` | `hospital123` | Bed shortage, patient placement |
| City Health Authority | `city` | `city123` | Compare wards and cities, review requests |
| Public | no login | no login | Public Advisory page |

These are fixed demonstration accounts, not production security. After sign-in every role can open every page.

## Features

- **Dashboard and Command Center:** risk summary, priority wards, schematic ward map with selectable layers.
- **Resources:** allocation of saline bags, diagnostic kits, beds and spraying crews under limited stock, with deficit alerts.
- **Overflow:** moves expected bed overflow to the least occupied ward in the same city, with a patient transfer desk.
- **Simulator:** estimated effect of vector control crews on cases 2 to 4 weeks ahead, with wards ranked by cases prevented per crew.
- **Dispatch:** SMS and WhatsApp text and printable HTML ward briefs. Nothing is sent automatically.
- **Public Advisory:** ward risk, health advice and a rule-based question and answer helper (not a chatbot model, not medical advice).
- **English and Bangla** toggle. Some map, table and message text stays in English.
- **Offline use:** a local run needs no external API. Data, models and templates are in the repository.

## Run Locally

Python 3.12 is recommended.

```bash
git clone https://github.com/wafaaah/Beyond-Binary.git
cd Beyond-Binary
python -m venv .venv
```

Activate (Windows PowerShell `.venv\Scripts\Activate.ps1`, Windows cmd `.venv\Scripts\activate`, Linux or macOS `source .venv/bin/activate`), then:

```bash
pip install -r requirements.txt
streamlit run dashboard/Dashboard.py
```

**Offline check:** install the packages once, turn the network off, then run the last command.

**Deployment:** Streamlit Community Cloud, branch `main`, main file `dashboard/Dashboard.py`, Python 3.12.

## Model and Results

Three `HistGradientBoostingRegressor` models (Poisson loss) predict weekly cases 2, 3 and 4 weeks ahead from lagged weather, season and ward features. Past case counts are not model inputs. The split is chronological: training targets up to 2022, validation to June 2024, testing from July 2024.

| Horizon | Test MAE | Baseline MAE (repeat latest week) | Test RMSE | Test R2 | MAE when cases are 10 or more |
|---|---:|---:|---:|---:|---:|
| 2 weeks | 1.54 | 2.04 | 2.91 | 0.53 | 4.24 |
| 3 weeks | 1.63 | 2.33 | 3.10 | 0.47 | 5.14 |
| 4 weeks | 1.57 | 2.58 | 2.97 | 0.51 | 4.62 |

Errors are clearly larger in high-case weeks.

Risk levels: Low below 1 case, Medium 1 to below 5, High 5 to below 10, Critical 10 or more.

## Exports

`exports/` holds sample outputs: a commissioner brief (HTML), SMS text and WhatsApp text.

## Assumptions and Limitations

- The dataset has no coordinates, hospitals, bed capacity, stock or crew data.
- Bed capacity is assumed to be the 90th percentile of each ward's past weekly bed demand.
- Crews required per ward: Low 0, Medium 1, High 2, Critical 3.
- Each city has its own supply pool. Crews form one shared pool.
- The simulator assumes each crew removes 25% of the remaining water logging and sanitation gap. Results are model estimates, not proof of cause and effect.
- Allocation is a priority rule, not an optimiser, so lower priority wards can receive nothing.
- Maps and distances are schematic.
- Requests and bed updates last only for the browser session. There is no database.
- The forecasts are not clinically or field validated and are not official outbreak warnings.

The default demonstration week (origin 12 August 2024) is the test-period week whose target had the most actual cases. This choice does not change model inputs.

## Data Sources

- Dengue dataset provided for the hackathon (weekly, 4 January 2016 to 29 December 2025), including the onsite version with supply demand columns.
- Weather scripts in the repository use the [Open-Meteo](https://open-meteo.com/) API. The running dashboard makes no weather API call.

## AI Assistance and External Resources Disclosure

- **Claude (Anthropic):** substantial help with Phase 2 code, interface design, SVG artwork and opening animation, English and Bangla text, and documentation drafts.
- **ChatGPT:** interface design reference images.
- **Logo:** generated with Microsoft Copilot.
- **Libraries:** Streamlit, pandas, NumPy, scikit-learn, joblib, Plotly, pydeck.
- The forecasts come from the team's scikit-learn models. The app calls no generative AI service.

## Project Structure

```text
Beyond-Binary/
├── dashboard/
│   ├── Dashboard.py        main page
│   ├── pages/              role, planning and public pages
│   └── *.py                interface, login, language and map modules
├── ml/                     features, training, allocation, routing, simulator, dispatch
├── models/                 saved 2, 3 and 4 week models
├── data/                   raw and processed data
├── exports/                sample outputs
├── requirements.txt
├── README.md
└── ARCHITECTURE.md
```

## Team

**Team Name:** Beyond-Binary  
**Hackathon:** EDU AI Engineering Hackathon 2026

| Member | ID |
|---|---|
| Aspia Khanam Wafa (Leader) | 233009512 |
| Saima Ajim | 233032112 |
| Kazi Elin Sanjida | 233015912 |
