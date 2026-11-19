-- Customer Analytics | MySQL 8.0
-- Audit of the cleaned, positive-transaction table.
-- Some zeros are expected because the source has already been cleaned in Python.
USE customer_analytics;

SELECT
    COUNT(*) AS total_rows,
    SUM(InvoiceNo IS NULL OR TRIM(InvoiceNo) = '') AS missing_invoice_no,
    SUM(StockCode IS NULL OR TRIM(StockCode) = '') AS missing_stockcode,
    SUM(Description IS NULL OR TRIM(Description) = '') AS missing_description,
    SUM(Quantity IS NULL) AS missing_quantity,
    SUM(InvoiceDate IS NULL) AS missing_invoice_date,
    SUM(UnitPrice IS NULL) AS missing_unitprice,
    SUM(CustomerID IS NULL OR TRIM(CustomerID) = '') AS missing_customerid,
    SUM(Country IS NULL OR TRIM(Country) = '') AS missing_country,
    SUM(Quantity <= 0) AS nonpositive_quantity,
    SUM(UnitPrice <= 0) AS nonpositive_price,
    SUM(InvoiceNo LIKE 'C%') AS cancelled_invoice_rows,
    COUNT(DISTINCT NULLIF(TRIM(CustomerID), '')) AS unique_customers,
    COUNT(DISTINCT NULLIF(TRIM(Country), '')) AS unique_countries,
    MIN(InvoiceDate) AS first_date,
    MAX(InvoiceDate) AS last_date
FROM sales_clean_full;
