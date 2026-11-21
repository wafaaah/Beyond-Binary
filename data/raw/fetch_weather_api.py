
import requests
import pandas as pd
from pathlib import Path

# Chattogram location
LATITUDE = 22.390158
LONGITUDE = 91.77019

# Historical weather API
URL = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "start_date": "2026-09-14",
    "end_date": "2026-11-21",
    "daily": [
        "precipitation_sum",
        "temperature_2m_mean",
        "temperature_2m_min",
        "temperature_2m_max",
        "relative_humidity_2m_mean"
    ],
    "timezone": "Asia/Dhaka"
}

try:
    print("Fetching weather data...")

    response = requests.get(URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    # Convert API response into DataFrame
    df = pd.DataFrame(data["daily"])

    # Rename columns
    df = df.rename(columns={
        "time": "date",
        "precipitation_sum": "rainfall_mm",
        "temperature_2m_mean": "avg_temp_c",
        "temperature_2m_min": "min_temp_c",
        "temperature_2m_max": "max_temp_c",
        "relative_humidity_2m_mean": "relative_humidity_pct"
    })

    # Save CSV
    project_root = Path(__file__).resolve().parents[2]

    output_path = (
        project_root / "data" / "raw" /
        "chattogram_weather_api.csv"
    )

    df.to_csv(output_path, index=False)

    print("\nWeather data fetched successfully!")
    print("Total records:", len(df))

    print("\nFirst 5 records:")
    print(df.head())

    print("\nAvailable columns:")
    print(df.columns.tolist())

    print("\nSaved at:", output_path)

except requests.exceptions.RequestException as error:
    print("API request failed:", error)

except Exception as error:
    print("Something went wrong:", error)
