import os
import time 
import requests
import pandas as pd

import os
import time
import requests
import pandas as pd


API_KEY = os.getenv("CENSUS_API_KEY")

if not API_KEY:
    raise ValueError("Set your Census API key first: export CENSUS_API_KEY='Put API key here'")

BASE_URL = "https://api.census.gov/data/timeseries/intltrade/imports/hs"

# First version: HS2-level critical import sectors
CRITICAL_HS2_CODES = {
    "30": "Pharmaceuticals",
    "26": "Critical minerals / ores",
    "75": "Nickel and articles",
    "76": "Aluminum and articles",
    "81": "Other base metals",
    "84": "Machinery / computers",
    "85": "Electronics / electrical machinery",
    "87": "Vehicles / auto parts",
    "90": "Medical / precision instruments",
}

def fetch_hs_imports(hs_code: str, sector: str) -> pd.DataFrame:
    params = {
        "get": "CTY_CODE,CTY_NAME,I_COMMODITY,I_COMMODITY_LDESC,GEN_VAL_MO,YEAR,MONTH,COMM_LVL",
        "time": "from 2021-01 to 2025-12",
        "SUMMARY_LVL": "DET",
        "COMM_LVL": "HS2",
        "I_COMMODITY": hs_code,
        "key": API_KEY,
    }

    response = requests.get(BASE_URL, params=params, timeout=60)
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    df["sector"] = sector
    return df

all_data = []

for hs_code, sector in CRITICAL_HS2_CODES.items():
    print(f"Downloading HS {hs_code}: {sector}")
    df = fetch_hs_imports(hs_code, sector)
    all_data.append(df)
    time.sleep(0.5)

imports = pd.concat(all_data, ignore_index=True)

imports["GEN_VAL_MO"] = pd.to_numeric(imports["GEN_VAL_MO"], errors="coerce")
imports["YEAR"] = imports["YEAR"].astype(int)
imports["MONTH"] = imports["MONTH"].astype(int)

imports.to_csv("us_critical_imports_2021_2025_raw.csv", index=False)

print("Done.")
print(imports.head())
print(imports.shape)

