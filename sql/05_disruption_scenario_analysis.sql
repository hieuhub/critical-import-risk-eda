/*
This file creates a disruption scenario view using the HS4 supplier concentration analysis.

Calculations:
1. Value at risk under a 30% top-supplier disruption
2. Value at risk under a 50% top-supplier disruption
3. Supplier concentration risk level from the previous SQL view

Note: 
- If the top supplier country for a critical product is disrupted,
how much import value is exposed?
- Disruption value at risk estimates the financial exposure if that dependency is disrupted.
*/
DROP VIEW IF EXISTS analytics.vw_hs4_disruption_scenario;

CREATE OR  REPLACE VIEW analytics.vw_hs4_disruption_scenario AS 

SELECT 
    product_group,
    hs_code,
    hs_description,
    top_supplier_country,
    total_product_import_value,
    top_supplier_import_value,
    top_supplier_share,
    concentration_risk_level,

    -- 30% discruption scenario 
    -- (How much import value is exposed if the top supplier's supply drops by 30%)
    top_supplier_import_value * 0.30 AS value_at_risk_30pct_disruption,

    -- 50% discruption scenario
    -- (More severe discruption where half of the top supplier's supply is lost)
    top_supplier_import_value * 0.50 AS value_at_risk_50pct_disruption

FROM analytics.vw_hs4_supplier_concentration;
