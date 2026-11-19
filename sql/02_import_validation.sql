-- Customer Analytics | MySQL 8.0
-- Run AFTER importing the cleaned sales CSV into sales_clean_full.
USE customer_analytics;

-- 1. Row count and positive-transaction value.
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT InvoiceNo) AS total_orders,
    COUNT(DISTINCT NULLIF(TRIM(CustomerID), '')) AS identifiable_customers,
    ROUND(SUM(Quantity * UnitPrice), 2) AS sales_value
FROM sales_clean_full;

-- 2. Reconcile identifiable vs unidentified transaction lines and amounts.
SELECT
    CASE
        WHEN CustomerID IS NULL OR TRIM(CustomerID) = ''
            THEN 'Unidentified customer'
        ELSE 'Identified customer'
    END AS customer_scope,
    COUNT(*) AS transaction_lines,
    ROUND(SUM(Quantity * UnitPrice), 2) AS sales_value
FROM sales_clean_full
GROUP BY customer_scope;

-- Expected for this project (as previously verified in Python):
-- Total lines 524,878; sales value 10,642,110.80.
-- Identified lines 392,692; unidentified lines 132,186.
-- IMPORTANT: These values describe positive transactions, NOT net revenue.
