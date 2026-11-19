-- Customer Analytics | MySQL 8.0
-- Run once before importing the cleaned positive-sales CSV.
-- No existing tables or records are deleted.

CREATE DATABASE IF NOT EXISTS customer_analytics
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE customer_analytics;

-- Import data/online_retail_sales_clean.csv into this table.
-- Column names and order match the cleaned CSV header.
CREATE TABLE IF NOT EXISTS sales_clean_full (
    InvoiceNo   VARCHAR(20),
    StockCode   VARCHAR(20),
    Description TEXT,
    Quantity    INT,
    InvoiceDate DATETIME,
    UnitPrice   DECIMAL(12, 4),
    CustomerID  VARCHAR(20),
    Country     VARCHAR(100),
    INDEX idx_invoice_date (InvoiceDate),
    INDEX idx_customer_id (CustomerID),
    INDEX idx_invoice_no (InvoiceNo)
) ENGINE=InnoDB
  DEFAULT CHARACTER SET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;

SELECT DATABASE() AS active_database;
SHOW TABLES;
