-- Customer Analytics | MySQL 8.0
-- Sales performance on sales_clean_full (positive transaction lines).
USE customer_analytics;

-- 1. Overall business KPIs.
SELECT
    COUNT(*) AS transaction_lines,
    COUNT(DISTINCT InvoiceNo) AS orders,
    COUNT(DISTINCT NULLIF(TRIM(CustomerID), '')) AS identifiable_customers,
    ROUND(SUM(Quantity * UnitPrice), 2) AS sales_value,
    ROUND(SUM(Quantity * UnitPrice) /
          NULLIF(COUNT(DISTINCT InvoiceNo), 0), 2) AS avg_order_value
FROM sales_clean_full;

-- 2. Month-over-month sales growth (MySQL 8 window function LAG).
WITH monthly_sales AS (
    SELECT
        DATE_FORMAT(InvoiceDate, '%Y-%m') AS sales_month,
        COUNT(DISTINCT InvoiceNo) AS orders,
        SUM(Quantity * UnitPrice) AS sales_value
    FROM sales_clean_full
    GROUP BY DATE_FORMAT(InvoiceDate, '%Y-%m')
), month_with_lag AS (
    SELECT
        sales_month, orders, sales_value,
        LAG(sales_value) OVER (ORDER BY sales_month) AS prior_month_sales
    FROM monthly_sales
)
SELECT
    sales_month,
    orders,
    ROUND(sales_value, 2) AS sales_value,
    ROUND(prior_month_sales, 2) AS prior_month_sales,
    ROUND(100 * (sales_value - prior_month_sales) /
          NULLIF(prior_month_sales, 0), 2) AS mom_growth_pct
FROM month_with_lag
ORDER BY sales_month;

-- 3. Top 5 months by positive sales value.
SELECT
    DATE_FORMAT(InvoiceDate, '%Y-%m') AS sales_month,
    COUNT(DISTINCT InvoiceNo) AS orders,
    ROUND(SUM(Quantity * UnitPrice), 2) AS sales_value
FROM sales_clean_full
GROUP BY DATE_FORMAT(InvoiceDate, '%Y-%m')
ORDER BY sales_value DESC
LIMIT 5;

-- 4. Top 5 months' average order value (AOV = sales / DISTINCT invoices).
SELECT
    DATE_FORMAT(InvoiceDate, '%Y-%m') AS sales_month,
    COUNT(DISTINCT InvoiceNo) AS orders,
    ROUND(SUM(Quantity * UnitPrice), 2) AS sales_value,
    ROUND(SUM(Quantity * UnitPrice) /
          NULLIF(COUNT(DISTINCT InvoiceNo), 0), 2) AS avg_order_value
FROM sales_clean_full
GROUP BY DATE_FORMAT(InvoiceDate, '%Y-%m')
ORDER BY sales_value DESC
LIMIT 5;

-- Interpretation caution: December 2011 contains only data through Dec 9.
-- Treat sales_value as positive-transaction amount; returns were excluded.
