import pandas as pd

df = pd.read_csv("eda_hs4_disruption_scenario.csv")

# Create percentile-based scores from 0-100
df["import_exposure_score"] = df["total_product_import_value"].rank(pct=True) * 100
df["concentration_score"] = df["top_supplier_share"].rank(pct=True) * 100
df["disruption_exposure_score"] = df["value_at_risk_30pct_disruption"].rank(pct=True) * 100

# Weighted final risk score
df["final_risk_score"] = (
    df["disruption_exposure_score"] * 0.40 +
    df["concentration_score"] * 0.35 +
    df["import_exposure_score"] * 0.25
)

# Priority label
def assign_priority(score):
    if score >= 75:
        return "High Priority"
    elif score >= 50:
        return "Medium Priority"
    else:
        return "Lower Priority"

df["diversification_priority"] = df["final_risk_score"].apply(assign_priority)

# Rank products
df = df.sort_values("final_risk_score", ascending=False)
df["risk_rank"] = range(1, len(df) + 1)

# Final output
final = df[
    [
        "risk_rank",
        "product_group",
        "hs_code",
        "top_supplier_country",
        "total_product_import_value",
        "top_supplier_import_value",
        "top_supplier_share",
        "value_at_risk_30pct_disruption",
        "value_at_risk_50pct_disruption",
        "concentration_risk_level",
        "final_risk_score",
        "diversification_priority"
    ]
]

final.to_csv("final_critical_import_risk_ranking.csv", index=False)

print("Final risk ranking saved.")
print(final)