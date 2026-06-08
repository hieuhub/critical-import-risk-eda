/*
Purpose:
Create a Tableau Public export view from the final HS4 risk ranking view.

Converts large dollar values into billions for cleaner dashboard labels.
*/


DROP VIEW IF EXISTS analytics.vw_tableau_final_risk_export;


CREATE OR REPLACE VIEW analytics.vw_tableau_final_risk_export AS

SELECT
    risk_rank,
    product_group,
    hs_code,
    top_supplier_country,

    -- Convert large dollar values into billions for Tableau.
    total_product_import_value / 1000000000 AS total_import_value_billions,
    top_supplier_import_value / 1000000000 AS top_supplier_import_value_billions,
    value_at_risk_30pct_disruption / 1000000000 AS value_at_risk_30pct_billions,
    value_at_risk_50pct_disruption / 1000000000 AS value_at_risk_50pct_billions,

    -- Supplier dependency metric.
    top_supplier_share,

    -- Risk scoring metrics.
    import_exposure_score,
    concentration_score,
    disruption_exposure_score,
    final_risk_score,

    -- priority label.
    diversification_priority

FROM analytics.vw_hs4_final_risk_ranking;