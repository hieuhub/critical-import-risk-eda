/* 
This file creates the final HS4 critical import risk ranking view. 

Combination of: 
1. Total product import exposure
2. Supplier concentration risk 
3. 30% disruption value at risk 
4. 50% disruption value at risk 
5. Final weighted risk 
6. Diversification priority label 

Notes:
- Which critical import products should be prioritized for supplier diversification? 
*/

-- Drop the old view first so new changes to column names or logic apply cleanly.

DROP VIEW IF EXISTS analytics.vw_hs4_final_risk_ranking;

CREATE OR REPLACE VIEW analytics.vw_hs4_final_risk_ranking AS

WITH scored_products AS (
    SELECT 
        product_group,
        hs_code,
        hs_description,
        top_supplier_country,
        total_product_import_value,
        top_supplier_import_value,
        top_supplier_share,
        concentration_risk_level,
        value_at_risk_30pct_disruption,
        value_at_risk_50pct_disruption,
-- Score 1: product size/exposure.
        -- Higher total import value means more business exposure.
        CUME_DIST() OVER (
            ORDER BY total_product_import_value
        ) * 100 AS import_exposure_score,

        -- Score 2: supplier concentration.
        -- Higher top supplier share means more dependency risk.
        CUME_DIST() OVER (
            ORDER BY top_supplier_share
        ) * 100 AS concentration_score,

        -- Score 3: disruption exposure.
        -- Higher value at risk means greater financial exposure under stress.
        CUME_DIST() OVER (
            ORDER BY value_at_risk_30pct_disruption
        ) * 100 AS disruption_exposure_score

    FROM analytics.vw_hs4_disruption_scenario
),

final_scores AS (
    SELECT
        *,

        -- Final weighted risk score.
        -- 40% disruption exposure: most directly answers "how much value is at risk?"
        -- 35% concentration: measures supplier dependency/fragility.
        -- 25% import exposure: measures overall product importance.
        (
            disruption_exposure_score * 0.40 +
            concentration_score * 0.35 +
            import_exposure_score * 0.25
        ) AS final_risk_score

    FROM scored_products
),

ranked_products AS (
    SELECT
        *,

        -- Rank products from highest risk to lowest risk.
        ROW_NUMBER() OVER (
            ORDER BY final_risk_score DESC
        ) AS risk_rank,

        -- Priority label for executive interpretation.
        CASE
            WHEN final_risk_score >= 75 THEN 'High Priority'
            WHEN final_risk_score >= 50 THEN 'Medium Priority'
            ELSE 'Lower Priority'
        END AS diversification_priority

    FROM final_scores
)

SELECT
    risk_rank,
    product_group,
    hs_code,
    hs_description,
    top_supplier_country,
    total_product_import_value,
    top_supplier_import_value,
    top_supplier_share,
    concentration_risk_level,
    value_at_risk_30pct_disruption,
    value_at_risk_50pct_disruption,
    import_exposure_score,
    concentration_score,
    disruption_exposure_score,
    final_risk_score,
    diversification_priority

FROM ranked_products;


/*
SELECT
    risk_rank,
    product_group,
    hs_code,
    top_supplier_country,
    ROUND(top_supplier_share::numeric, 3) AS top_supplier_share,
    ROUND(value_at_risk_30pct_disruption / 1000000000, 2) AS value_at_risk_30pct_billions,
    ROUND(final_risk_score::numeric, 1) AS final_risk_score,
    diversification_priority
FROM analytics.vw_hs4_final_risk_ranking
ORDER BY risk_rank;

I'm running this in psql to check the view if it's correct

*/




