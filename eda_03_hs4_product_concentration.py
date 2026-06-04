import pandas as pd

df = pd.read_csv("us_critical_imports_hs4_cleaned.csv")

# Safety filter: remove aggregate rows if any slipped through
df["supplier_country"] = df["supplier_country"].astype(str).str.strip()
df = df[~df["supplier_country"].str.upper().str.contains("TOTAL", na=False)]

# Total import value by HS4 product
product_totals = (
    df.groupby(["product_group", "hs_code", "hs_description"])["import_value_usd"]
    .sum()
    .reset_index(name="total_product_import_value")
)

# Import value by product + supplier country
product_supplier = (
    df.groupby(["product_group", "hs_code", "hs_description", "supplier_country"])["import_value_usd"]
    .sum()
    .reset_index(name="supplier_import_value")
)

# Rank suppliers within each product
product_supplier["supplier_rank"] = (
    product_supplier.groupby("hs_code")["supplier_import_value"]
    .rank(method="first", ascending=False)
)

# Keep top supplier for each product
top_product_suppliers = product_supplier[product_supplier["supplier_rank"] == 1].copy()

# Merge with product totals
concentration = top_product_suppliers.merge(
    product_totals,
    on=["product_group", "hs_code", "hs_description"]
)

# Calculate concentration share
concentration["top_supplier_share"] = (
    concentration["supplier_import_value"] /
    concentration["total_product_import_value"]
)

# Risk label
def classify_risk(share):
    if share >= 0.50:
        return "High"
    elif share >= 0.30:
        return "Medium"
    else:
        return "Low"

concentration["concentration_risk_level"] = concentration["top_supplier_share"].apply(classify_risk)

# Clean final table
concentration = concentration.rename(columns={
    "supplier_country": "top_supplier_country",
    "supplier_import_value": "top_supplier_import_value"
})

concentration = concentration[
    [
        "product_group",
        "hs_code",
        "hs_description",
        "top_supplier_country",
        "total_product_import_value",
        "top_supplier_import_value",
        "top_supplier_share",
        "concentration_risk_level"
    ]
].sort_values(["concentration_risk_level", "top_supplier_share"], ascending=[True, False])

# Better sorting: High first, then Medium, then Low
risk_order = {"High": 1, "Medium": 2, "Low": 3}
concentration["risk_sort"] = concentration["concentration_risk_level"].map(risk_order)

concentration = (
    concentration
    .sort_values(["risk_sort", "top_supplier_share"], ascending=[True, False])
    .drop(columns="risk_sort")
)

concentration.to_csv("eda_hs4_product_concentration.csv", index=False)

print("HS4 product concentration saved.")
print(concentration)