/*
This file validates that the cleaned HS4 import dataset loaded correctly into Postgres.

Checking:
1. Total row count
2. Date coverage
3. Number of product groups and supplier countries
4. Total import value
5. Top imported critical products by value
*/

SELECT 
    COUNT(*) AS row_count
FROM analytics.imports_hs4;


--Check high-level dataset health
-- start_date/end_date, confirm the time period.
-- product_groups, confirms the HS4 critical product categories loaded.
-- supplier_countries, confirms country-level supplier analysis is possible.
-- total_import_value, confirms import values are present and numeric.

SELECT
    MIN(date) AS start_date,
    MAX(date) AS end_date,
    COUNT(DISTINCT product_group) AS product_groups,
    COUNT(DISTINCT supplier_country) AS supplier_countries,
    SUM(import_value_usd) AS total_import_value
FROM analytics.imports_hs4;

--Check total import value by product group
-- Identify which HS4 products have the largest import exposure.

SELECT
    product_group,
    hs_code,
    SUM(import_value_usd) AS total_import_value
    FROM analytics.imports_hs4
    GROUP BY product_group, hs_code
    ORDER BY total_import_value DESC;

--Preview before loading
SELECT *
FROM analytics.imports_hs4
LIMIT 10; 




