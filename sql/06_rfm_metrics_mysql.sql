-- Customer Analytics | MySQL 8.0
-- Compute RFM metrics independently in SQL for cross-checking Python.
-- Recency uses last dataset timestamp + 1 day, matching Python's reference
-- datetime and TIMESTAMPDIFF(DAY, ...) whole-day behavior.
USE customer_analytics;

WITH snapshot AS (
    SELECT DATE_ADD(MAX(InvoiceDate), INTERVAL 1 DAY) AS snapshot_at
    FROM sales_clean_full
), customer_lines AS (
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
    c.customer_id,
    TIMESTAMPDIFF(DAY, MAX(c.InvoiceDate), s.snapshot_at) AS Recency,
    COUNT(DISTINCT c.InvoiceNo) AS Frequency,
    ROUND(SUM(c.Quantity * c.UnitPrice), 2) AS Monetary
FROM customer_lines AS c
CROSS JOIN snapshot AS s
GROUP BY c.customer_id, s.snapshot_at
ORDER BY Monetary DESC;

-- Expected customer count for this project: 4,338.
-- Compare total Monetary against 8,887,208.89 (allow rounding tolerance).
