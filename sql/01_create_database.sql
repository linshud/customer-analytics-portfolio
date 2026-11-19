-- Customer Analytics | MySQL 8.0
-- Run once before creating/importing the sales_clean_full table.
-- No existing tables or records are deleted.

CREATE DATABASE IF NOT EXISTS customer_analytics
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE customer_analytics;
SELECT DATABASE() AS active_database;
