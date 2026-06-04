-- creates the Postgres table for the cleaned HS4 import data. 

CREATE SCHEMA IF NOT EXISTS analytics;

DROP TABLE IF EXISTS analytics.imports_hs4; 

CREATE TABLE analytics.imports_hs4 (
    date DATE, 
    year INT, 
    month INT,
    product_group TEXT,
    hs_code TEXT,
    hs_description TEXT,
    supplier_country TEXT,
    country_code TEXT,
    import_value_usd NUMERIC,
    commodity_level TEXT
);