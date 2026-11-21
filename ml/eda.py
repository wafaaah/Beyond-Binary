import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = "data/processed/cleaned_dengue.csv"

df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])

# 1. Dengue cases over time
plt.figure()
plt.plot(df["date"], df["dengue_cases"])
plt.title("Dengue Cases Over Time")
plt.xlabel("Date")
plt.ylabel("Dengue Cases")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 2. Rainfall vs dengue cases
plt.figure()
plt.scatter(df["rainfall_mm"], df["dengue_cases"])
plt.title("Rainfall vs Dengue Cases")
plt.xlabel("Rainfall (mm)")
plt.ylabel("Dengue Cases")
plt.tight_layout()
plt.show()

# 3. Temperature vs cases
plt.figure()
plt.scatter(df["avg_temp_c"], df["dengue_cases"])
plt.title("Average Temperature vs Dengue Cases")
plt.xlabel("Average Temperature (C)")
plt.ylabel("Dengue Cases")
plt.tight_layout()
plt.show()

# 4. Humidity vs cases
plt.figure()
plt.scatter(df["relative_humidity_pct"], df["dengue_cases"])
plt.title("Humidity vs Dengue Cases")
plt.xlabel("Relative Humidity (%)")
plt.ylabel("Dengue Cases")
plt.tight_layout()
plt.show()

# 5. Correlation
numeric_df = df.select_dtypes(include="number")
correlation = numeric_df.corr()

print("\n========== CORRELATION ==========")
print(correlation["dengue_cases"].sort_values(ascending=False))

plt.figure()
plt.imshow(correlation, aspect="auto")
plt.xticks(range(len(correlation.columns)), correlation.columns, rotation=90)
plt.yticks(range(len(correlation.columns)), correlation.columns)
plt.title("Feature Correlation")
plt.colorbar()
plt.tight_layout()
plt.show()