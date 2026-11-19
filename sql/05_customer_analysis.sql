-- Customer Analytics | MySQL 8.0
-- Identifiable customer spend on cleaned positive transactions.
USE customer_analytics;

-- Top 10 customers by monetary contribution.
-- CustomerID in this CSV may be stored as text such as '17850.0'.
-- Trimming a final .0 gives a consistent display key for reporting.
WITH customer_lines AS (
    SELECT
        CASE
            WHEN RIGHT(TRIM(CustomerID), 2) = '.0'
                THEN LEFT(TRIM(CustomerID), CHAR_LENGTH(TRIM(CustomerID)) - 2)
            ELSE TRIM(CustomerID)
        END AS customer_id,
        InvoiceNo, InvoiceDate, Quantity, UnitPrice
    FROM sales_clean_full
    WHERE NULLIF(TRIM(CustomerID), '') IS NOT NULL
)
SELECT
    customer_id,
    COUNT(DISTINCT InvoiceNo) AS total_orders,
    ROUND(SUM(Quantity * UnitPrice), 2) AS total_spend,
    ROUND(SUM(Quantity * UnitPrice) /
          NULLIF(COUNT(DISTINCT InvoiceNo), 0), 2) AS avg_order_value,
    MIN(InvoiceDate) AS first_purchase_date,
    MAX(InvoiceDate) AS last_purchase_date
FROM customer_lines
GROUP BY customer_id
ORDER BY total_spend DESC
LIMIT 10;
