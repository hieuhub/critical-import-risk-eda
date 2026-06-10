import pandas as pd

df = pd.read_csv("us_critical_imports_hs4_cleaned.csv")

# Clean supplier names
df["supplier_country"] = df["supplier_country"].astype(str).str.strip()
df = df[~df["supplier_country"].str.upper().str.contains("TOTAL", na=False)]

# Use latest available year
latest_year = df["year"].max()
df_latest = df[df["year"] == latest_year].copy()

# Total import value by product
product_totals = (
    df_latest.groupby(["product_group", "hs_code", "hs_description"])["import_value_usd"]
    .sum()
    .reset_index(name="total_product_import_value")
)

# Import value by product + supplier
product_supplier = (
    df_latest.groupby(["product_group", "hs_code", "hs_description", "supplier_country"])["import_value_usd"]
    .sum()
    .reset_index(name="supplier_import_value")
)

# Rank suppliers for each product
product_supplier["supplier_rank"] = (
    product_supplier.groupby("hs_code")["supplier_import_value"]
    .rank(method="first", ascending=False)
)

# Top supplier per product
top_suppliers = product_supplier[product_supplier["supplier_rank"] == 1].copy()

# Merge total product value
scenario = top_suppliers.merge(
    product_totals,
    on=["product_group", "hs_code", "hs_description"]
)

# Concentration share
scenario["top_supplier_share"] = (
    scenario["supplier_import_value"] / scenario["total_product_import_value"]
)

# Disruption scenarios
scenario["value_at_risk_30pct_disruption"] = scenario["supplier_import_value"] * 0.30
scenario["value_at_risk_50pct_disruption"] = scenario["supplier_import_value"] * 0.50

# Risk level
def classify_risk(share):
    if share >= 0.50:
        return "High"
    elif share >= 0.30:
        return "Medium"
    else:
        return "Low"

scenario["concentration_risk_level"] = scenario["top_supplier_share"].apply(classify_risk)

# Rename columns
scenario = scenario.rename(columns={
    "supplier_country": "top_supplier_country",
    "supplier_import_value": "top_supplier_import_value"
})

# Final table
scenario = scenario[
    [
        "product_group",
        "hs_code",
        "hs_description",
        "top_supplier_country",
        "total_product_import_value",
        "top_supplier_import_value",
        "top_supplier_share",
        "concentration_risk_level",
        "value_at_risk_30pct_disruption",
        "value_at_risk_50pct_disruption"
    ]
].sort_values("value_at_risk_30pct_disruption", ascending=False)

scenario.to_csv("eda_hs4_disruption_scenario.csv", index=False)

print(f"Disruption scenario saved for year: {latest_year}")
print(scenario)