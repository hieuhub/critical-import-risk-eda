import pandas as pd

df = pd.read_csv("us_critical_imports_cleaned.csv")

# Total import value by sector
sector_totals = (
    df.groupby("sector")["import_value_usd"]
    .sum()
    .reset_index(name="total_sector_import_value")
)

# Import value by sector + supplier country
sector_supplier = (
    df.groupby(["sector", "supplier_country"])["import_value_usd"]
    .sum()
    .reset_index(name="supplier_import_value")
)

# Rank suppliers inside each sector
sector_supplier["supplier_rank"] = (
    sector_supplier.groupby("sector")["supplier_import_value"]
    .rank(method="first", ascending=False)
)

# Keep top supplier per sector
top_suppliers = sector_supplier[sector_supplier["supplier_rank"] == 1].copy()

# Merge with sector totals
concentration = top_suppliers.merge(sector_totals, on="sector")

# Calculate top supplier share
concentration["top_supplier_share"] = (
    concentration["supplier_import_value"] /
    concentration["total_sector_import_value"]
)

# Assign concentration risk level
def classify_risk(share):
    if share >= 0.50:
        return "High"
    elif share >= 0.30:
        return "Medium"
    else:
        return "Low"

concentration["concentration_risk_level"] = concentration["top_supplier_share"].apply(classify_risk)

# Format for readability
concentration = concentration.rename(columns={
    "supplier_country": "top_supplier_country",
    "supplier_import_value": "top_supplier_import_value"
})

concentration = concentration[
    [
        "sector",
        "top_supplier_country",
        "total_sector_import_value",
        "top_supplier_import_value",
        "top_supplier_share",
        "concentration_risk_level"
    ]
].sort_values("top_supplier_share", ascending=False)

# Save output
concentration.to_csv("eda_supplier_concentration_by_sector.csv", index=False)

print("Supplier concentration analysis saved.")
print(concentration)