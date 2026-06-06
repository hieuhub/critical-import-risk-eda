/*
This file calculate supplier concentration risk for HS4-level critical import products.

Identifying:
1. Total import value by product
2. Import value by product + supplier country
3. Top supplier country for each product
4. Top supplier share
5. Concentration risk level

6. Question: Which critical products are most dependent on one supplier country?

Note for myself: 
- A product with high import value is not automatically risky.
It becomes more fragile when a large share of that product comes from one country.
*/

CREATE OR REPLACE VIEW analytics.vw_hs4_supplier_concentration AS

WITH 

latest_year AS (
    --Using the latest year to represent current supply-chain exposure;
    SELECT MAX(year) AS year
    FROM analytics.imports_hs4
),

latest_imports AS (
    --Keep only the records from the latest year.
    SELECT i.*
    FROM analytics.imports_hs4 i 
    JOIN latest_year ly
        ON i.year = ly.year
),

product_totals AS (
    --Calculate total annual import value for each HS4 product
    SELECT 
        product_group,
        hs_code,
        hs_description,
        SUM(import_value_usd) AS total_product_import_value
    FROM latest_imports
    GROUP BY product_group, hs_code, hs_description
),

supplier_totals AS (
    --Calculate annual import value by product and supplier country.
    SELECT
        product_group,
        hs_code,
        hs_description,
        supplier_country,
        SUM(import_value_usd) AS supplier_import_value
    FROM latest_imports
    GROUP BY product_group, hs_code, hs_description, supplier_country
),

ranked_suppliers AS (
    --Rank suppliers within each product by import value.
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY hs_code
            ORDER  BY supplier_import_value DESC
        ) AS supplier_rank
    FROM supplier_totals
),

top_suppliers AS (
    -- Keep only the largest supplier country for each product.
    SELECT
        product_group,
        hs_code,
        hs_description,
        supplier_country AS top_supplier_country,
        supplier_import_value AS top_supplier_import_value
    FROM ranked_suppliers
    WHERE supplier_rank = 1
)

SELECT
    ts.product_group,
    ts.hs_code,
    ts.hs_description,
    ts.top_supplier_country,
    pt.total_product_import_value,
    ts.top_supplier_import_value,

    -- Top supplier share shows how dependent the product is on one country.
    ts.top_supplier_import_value / NULLIF(pt.total_product_import_value, 0) AS top_supplier_share,

    -- Risk category based on supplier concentration.
    CASE
        WHEN ts.top_supplier_import_value / NULLIF(pt.total_product_import_value, 0) >= 0.50 THEN 'High'
        WHEN ts.top_supplier_import_value / NULLIF(pt.total_product_import_value, 0) >= 0.30 THEN 'Medium'
        ELSE 'Low'
    END AS concentration_risk_level

FROM top_suppliers ts
JOIN product_totals pt
    ON ts.product_group = pt.product_group
    AND ts.hs_code = pt.hs_code
    AND ts.hs_description = pt.hs_description;


