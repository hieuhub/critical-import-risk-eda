import os
import time
import requests
import pandas as pd

API_KEY = os.getenv("CENSUS_API_KEY")

if not API_KEY:
    raise ValueError("Set API key first in Terminal.")

BASE_URL = "https://api.census.gov/data/timeseries/intltrade/imports/hs"

CRITICAL_HS4_CODES = {
    "3002": "Vaccines / blood / biological products",
    "3004": "Medicaments",
    "8471": "Computers / data processing machines",
    "8473": "Computer parts",
    "8504": "Transformers / power converters",
    "8507": "Batteries / energy storage",
    "8517": "Telecom equipment",
    "8534": "Printed circuits",
    "8541": "Semiconductor devices",
    "8542": "Integrated circuits",
    "8544": "Insulated wires / cables",
    "8708": "Auto parts",
    "9018": "Medical instruments",
    "9021": "Orthopedic / medical appliances",
    "7502": "Unwrought nickel",
    "7601": "Unwrought aluminum",
    "8105": "Cobalt articles",
}

def fetch_hs4_imports(hs_code, product_group):
    params = {
        "get": "CTY_CODE,CTY_NAME,I_COMMODITY_LDESC,GEN_VAL_MO,YEAR,MONTH",
        "time": "from 2021-01 to 2025-12",
        "SUMMARY_LVL": "DET",
        "COMM_LVL": "HS4",
        "I_COMMODITY": hs_code,
        "key": API_KEY,
    }

    response = requests.get(BASE_URL, params=params, timeout=60)
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])

    df["hs_code"] = hs_code
    df["commodity_level"] = "HS4"
    df["product_group"] = product_group

    return df

all_data = []

for hs_code, product_group in CRITICAL_HS4_CODES.items():
    print(f"Downloading HS4 {hs_code}: {product_group}")
    df = fetch_hs4_imports(hs_code, product_group)
    all_data.append(df)
    time.sleep(0.5)

imports = pd.concat(all_data, ignore_index=True)

imports = imports.rename(columns={
    "CTY_CODE": "country_code",
    "CTY_NAME": "supplier_country",
    "I_COMMODITY_LDESC": "hs_description",
    "GEN_VAL_MO": "import_value_usd",
    "YEAR": "year",
    "MONTH": "month"
})

imports["supplier_country"] = imports["supplier_country"].astype(str).str.strip()
imports = imports[~imports["supplier_country"].str.upper().str.contains("TOTAL", na=False)]

imports["import_value_usd"] = pd.to_numeric(imports["import_value_usd"], errors="coerce")
imports["year"] = pd.to_numeric(imports["year"], errors="coerce").astype("Int64")
imports["month"] = pd.to_numeric(imports["month"], errors="coerce").astype("Int64")
imports["hs_code"] = imports["hs_code"].astype(str).str.zfill(4)

imports["date"] = pd.to_datetime(
    imports["year"].astype(str) + "-" + imports["month"].astype(str) + "-01",
    errors="coerce"
)

imports = imports.dropna(subset=["supplier_country", "hs_code", "import_value_usd", "date"])
imports = imports[imports["import_value_usd"] > 0]

imports = imports[
    [
        "date",
        "year",
        "month",
        "product_group",
        "hs_code",
        "hs_description",
        "supplier_country",
        "country_code",
        "import_value_usd",
        "commodity_level"
    ]
]

imports.to_csv("us_critical_imports_hs4_cleaned.csv", index=False)

print("HS4 cleaned data saved.")
print("Rows:", len(imports))
print("Total import value:", f"${imports['import_value_usd'].sum():,.0f}")
print("Products:", imports["product_group"].nunique())
print("Supplier countries:", imports["supplier_country"].nunique())
print(imports.head())