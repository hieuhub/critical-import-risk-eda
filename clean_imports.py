import pandas as pd

# Load raw file
df = pd.read_csv("us_critical_imports_2021_2025_raw.csv")

# Rename columns
df = df.rename(columns={
    "CTY_CODE": "country_code",
    "CTY_NAME": "supplier_country",
    "I_COMMODITY": "hs_code",
    "I_COMMODITY_LDESC": "hs_description",
    "GEN_VAL_MO": "import_value_usd",
    "YEAR": "year",
    "MONTH": "month",
    "COMM_LVL": "commodity_level"
})

# Clean data types
df["import_value_usd"] = pd.to_numeric(df["import_value_usd"], errors="coerce")
df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
df["month"] = pd.to_numeric(df["month"], errors="coerce").astype("Int64")
df["hs_code"] = df["hs_code"].astype(str).str.zfill(2)

# Create date column
df["date"] = pd.to_datetime(
    df["year"].astype(str) + "-" + df["month"].astype(str) + "-01",
    errors="coerce"
)

# Remove invalid rows
df = df.dropna(subset=["supplier_country", "hs_code", "import_value_usd", "date"])

# Remove Census aggregate country rows
df = df[df["supplier_country"].str.upper() != "TOTAL FOR ALL COUNTRIES"]
df = df[df["country_code"].astype(str) != "0000"]

# Remove zero or negative import values
df = df[df["import_value_usd"] > 0]

# Reorder columns
df = df[
    [
        "date",
        "year",
        "month",
        "sector",
        "hs_code",
        "hs_description",
        "supplier_country",
        "country_code",
        "import_value_usd",
        "commodity_level"
    ]
]

# Save cleaned file
df.to_csv("us_critical_imports_cleaned.csv", index=False)

# Basic validation summary
print("Cleaned data saved.")
print("Rows:", len(df))
print("Date range:", df["date"].min(), "to", df["date"].max())
print("Total import value:", round(df["import_value_usd"].sum(), 2))
print("Number of supplier countries:", df["supplier_country"].nunique())
print("Sectors:", df["sector"].nunique())

print("\nPreview:")
print(df.head())