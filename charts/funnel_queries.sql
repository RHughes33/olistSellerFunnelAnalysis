-- ============================================================
-- Olist Seller Funnel Analysis
-- Stage 1: Marketing Qualified Lead (MQL) generated
-- Stage 2: Deal Closed / Won (lead becomes an onboarded seller)
-- Stage 3: First Sale (seller lists a product that actually sells)
-- ============================================================

-- Overall funnel counts
WITH stage1 AS (
    SELECT COUNT(*) AS n FROM mql
),
stage2 AS (
    SELECT COUNT(DISTINCT mql_id) AS n FROM closed_deals
),
stage3 AS (
    SELECT COUNT(DISTINCT cd.mql_id) AS n
    FROM closed_deals cd
    JOIN order_items oi ON oi.seller_id = cd.seller_id
)
SELECT
    (SELECT n FROM stage1) AS leads,
    (SELECT n FROM stage2) AS deals_won,
    (SELECT n FROM stage3) AS sellers_with_first_sale;


-- Funnel with conversion % at each step
SELECT
    'Lead (MQL)' AS stage, (SELECT COUNT(*) FROM mql) AS count, 1.0 AS pct_of_total
UNION ALL
SELECT
    'Deal Won', (SELECT COUNT(DISTINCT mql_id) FROM closed_deals),
    ROUND((SELECT COUNT(DISTINCT mql_id) FROM closed_deals) * 1.0 / (SELECT COUNT(*) FROM mql), 4)
UNION ALL
SELECT
    'First Sale',
    (SELECT COUNT(DISTINCT cd.mql_id) FROM closed_deals cd JOIN order_items oi ON oi.seller_id = cd.seller_id),
    ROUND((SELECT COUNT(DISTINCT cd.mql_id) FROM closed_deals cd JOIN order_items oi ON oi.seller_id = cd.seller_id) * 1.0 / (SELECT COUNT(*) FROM mql), 4);


-- Conversion rate (Lead -> Deal Won) segmented by lead origin
SELECT
    m.origin,
    COUNT(DISTINCT m.mql_id) AS leads,
    COUNT(DISTINCT cd.mql_id) AS deals_won,
    ROUND(COUNT(DISTINCT cd.mql_id) * 1.0 / COUNT(DISTINCT m.mql_id), 4) AS conversion_rate
FROM mql m
LEFT JOIN closed_deals cd ON cd.mql_id = m.mql_id
GROUP BY m.origin
ORDER BY leads DESC;


-- Conversion rate (Deal Won -> First Sale) segmented by business_segment
SELECT
    cd.business_segment,
    COUNT(DISTINCT cd.mql_id) AS deals_won,
    COUNT(DISTINCT CASE WHEN oi.seller_id IS NOT NULL THEN cd.mql_id END) AS reached_first_sale,
    ROUND(COUNT(DISTINCT CASE WHEN oi.seller_id IS NOT NULL THEN cd.mql_id END) * 1.0
          / COUNT(DISTINCT cd.mql_id), 4) AS conversion_rate
FROM closed_deals cd
LEFT JOIN order_items oi ON oi.seller_id = cd.seller_id
WHERE cd.business_segment IS NOT NULL
GROUP BY cd.business_segment
HAVING deals_won >= 10
ORDER BY deals_won DESC;
