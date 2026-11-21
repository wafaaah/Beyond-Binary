import pandas as pd

RAW_PATH = "data/raw/dengue_dataset.csv"
PROCESSED_PATH = "data/processed/cleaned_dengue.csv"

def load_and_clean_data():
    df = pd.read_csv(RAW_PATH)

    # Standardize column names
    df.columns = df.columns.str.strip()

    # Convert date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Remove rows with invalid dates or missing essential values
    df = df.dropna(subset=["date", "ward_id", "dengue_cases"])

    # Remove duplicate ward-date records
    df = df.drop_duplicates(subset=["ward_id", "date"])

    # Sort chronologically within each ward
    df = df.sort_values(["ward_id", "date"]).reset_index(drop=True)

    # Ensure dengue cases are numeric
    df["dengue_cases"] = pd.to_numeric(
        df["dengue_cases"], errors="coerce"
    )

    # Remove invalid target rows
    df = df.dropna(subset=["dengue_cases"])

    # Case count cannot be negative
    df = df[df["dengue_cases"] >= 0]

    # Save cleaned data
    df.to_csv(PROCESSED_PATH, index=False)

    print("Cleaning completed!")
    print("Cleaned shape:", df.shape)
    print("Saved to:", PROCESSED_PATH)

    return df


if __name__ == "__main__":
    load_and_clean_data()