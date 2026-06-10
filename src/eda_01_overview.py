import pandas as pd

df = pd.read_csv("us_critical_imports_cleaned.csv")
df["date"] = pd.to_datetime(df["date"])

# 1. Basic dataset overview
print("Rows:", len(df))
print("Date range:", df["date"].min(), "to", df["date"].max())
print("Total import value:", f"${df['import_value_usd'].sum():,.0f}")
print("Supplier countries:", df["supplier_country"].nunique())
print("Sectors:", df["sector"].nunique())

# 2. Total imports by year
imports_by_year = (
    df.groupby("year")["import_value_usd"]
    .sum()
    .reset_index()
    .sort_values("year")
)

print("\nImports by year:")
print(imports_by_year)

# 3. Total imports by sector
imports_by_sector = (
    df.groupby("sector")["import_value_usd"]
    .sum()
    .reset_index()
    .sort_values("import_value_usd", ascending=False)
)

print("\nImports by sector:")
print(imports_by_sector)

# 4. Top supplier countries overall
top_suppliers = (
    df.groupby("supplier_country")["import_value_usd"]
    .sum()
    .reset_index()
    .sort_values("import_value_usd", ascending=False)
    .head(15)
)

print("\nTop 15 supplier countries:")
print(top_suppliers)

# Save outputs
imports_by_year.to_csv("eda_imports_by_year.csv", index=False)
imports_by_sector.to_csv("eda_imports_by_sector.csv", index=False)
top_suppliers.to_csv("eda_top_suppliers.csv", index=False)

print("\nEDA overview files saved.")