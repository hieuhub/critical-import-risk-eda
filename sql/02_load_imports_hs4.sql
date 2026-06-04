-- this is a load script to load cleaned CSV into Postgres
\copy analytics.imports_hs4 FROM '/Users/HieuNg/Desktop/EDA/us_critical_imports_hs4_cleaned.csv' WITH (FORMAT csv, HEADER true);


