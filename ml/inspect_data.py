import pandas as pd

DATA_PATH = "data/raw/dengue_dataset.csv"

df = pd.read_csv(DATA_PATH)

print("\n========== DATASET INFO ==========")
print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\n========== FIRST 5 ROWS ==========")
print(df.head())

print("\n========== DATA TYPES ==========")
print(df.dtypes)

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

print("\n========== DUPLICATE ROWS ==========")
print(df.duplicated().sum())

print("\n========== WARD COUNT ==========")
print(df["ward_id"].nunique())
print(df["ward_id"].value_counts())

print("\n========== DATE RANGE ==========")
df["date"] = pd.to_datetime(df["date"], errors="coerce")
print("Start:", df["date"].min())
print("End:", df["date"].max())

print("\n========== CASE STATISTICS ==========")
print(df["dengue_cases"].describe())

print("\n========== CASE DISTRIBUTION ==========")
print(df["dengue_cases"].value_counts().sort_index())