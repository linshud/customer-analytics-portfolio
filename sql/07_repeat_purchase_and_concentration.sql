-- Customer Analytics | MySQL 8.0
-- Repeat purchasing and monetary concentration among identifiable customers.
USE customer_analytics;

-- 1. Distinct-invoice purchase frequency per customer.
WITH customer_orders AS (
    SELECT
        CustomerID,
        COUNT(DISTINCT InvoiceNo) AS order_count
    FROM sales_clean_full
    WHERE NULLIF(TRIM(CustomerID), '') IS NOT NULL
    GROUP BY CustomerID
)
SELECT
    COUNT(*) AS customers,
    SUM(order_count = 1) AS single_order_customers,
    SUM(order_count >= 2) AS repeat_customers,
    ROUND(100 * SUM(order_count >= 2) / NULLIF(COUNT(*), 0), 2)
        AS repeat_customer_pct
FROM customer_orders;

-- 2. How much of identified-customer spending comes from the top 20%?
-- Percentiles are based on customer ranking, not on the RFM segment rules.
WITH customer_spend AS (
    SELECT
        CustomerID,
        SUM(Quantity * UnitPrice) AS spend
    FROM sales_clean_full
    WHERE NULLIF(TRIM(CustomerID), '') IS NOT NULL
    GROUP BY CustomerID
), ranked AS (
    SELECT
        CustomerID, spend,
        ROW_NUMBER() OVER (ORDER BY spend DESC, CustomerID) AS rn,
        COUNT(*) OVER () AS customer_count
    FROM customer_spend
)
SELECT
    COUNT(*) AS identifiable_customers,
    SUM(rn <= CEIL(0.20 * customer_count)) AS customers_in_top_20pct,
    ROUND(100 * SUM(CASE WHEN rn <= CEIL(0.20 * customer_count)
                         THEN spend ELSE 0 END) /
          NULLIF(SUM(spend), 0), 2) AS top_20pct_spending_share
FROM ranked;
