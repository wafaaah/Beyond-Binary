
import requests
import pandas as pd
from pathlib import Path

# Five city locations (approximate city-center coordinates)
CITIES = {
    "Chattogram": {
        "latitude": 22.3569,
        "longitude": 91.7832
    },
    "Dhaka North": {
        "latitude": 23.8103,
        "longitude": 90.4125
    },
    "Dhaka South": {
        "latitude": 23.7104,
        "longitude": 90.4074
    },
    "Gazipur": {
        "latitude": 24.0023,
        "longitude": 90.4264
    },
    "Narayanganj": {
        "latitude": 23.6238,
        "longitude": 90.4990
    }
}

URL = "https://archive-api.open-meteo.com/v1/archive"

START_DATE = "2026-09-14"
END_DATE = "2026-11-21"

DAILY_VARIABLES = [
    "precipitation_sum",
    "temperature_2m_mean",
    "temperature_2m_min",
    "temperature_2m_max",
    "relative_humidity_2m_mean"
]

all_city_data = []

try:
    print("Starting weather data collection...\n")

    for city, coordinates in CITIES.items():

        print(f"Fetching weather for {city}...")

        params = {
            "latitude": coordinates["latitude"],
            "longitude": coordinates["longitude"],
            "start_date": START_DATE,
            "end_date": END_DATE,
            "daily": DAILY_VARIABLES,
            "timezone": "Asia/Dhaka"
        }

        response = requests.get(
            URL,
            params=params,
            timeout=30
        )

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

        # Add city name
        df["city"] = city

        all_city_data.append(df)

        print(f"  Records collected: {len(df)}")

    # Combine all cities
    final_df = pd.concat(
        all_city_data,
        ignore_index=True
    )

    # Arrange columns
    final_df = final_df[
        [
            "date",
            "city",
            "rainfall_mm",
            "avg_temp_c",
            "min_temp_c",
            "max_temp_c",
            "relative_humidity_pct"
        ]
    ]

    # Save CSV
    project_root = Path(__file__).resolve().parents[2]

    output_path = (
        project_root / "data" / "raw" /
        "city_weather_api.csv"
    )

    final_df.to_csv(output_path, index=False)

    print("\nAll city weather data collected successfully!")

    print("\nTotal records:", len(final_df))

    print("\nRecords by city:")
    print(final_df.groupby("city").size())

    print("\nFirst 10 records:")
    print(final_df.head(10).to_string(index=False))

    print("\nSaved at:", output_path)

except requests.exceptions.RequestException as error:
    print("\nAPI request failed:", error)

except Exception as error:
    print("\nSomething went wrong:", error)
