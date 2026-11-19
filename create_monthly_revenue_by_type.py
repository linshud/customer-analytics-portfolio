"""Create the monthly New/Returning revenue CSV used by the existing Power BI report.

Place next to your data/ folder and run:
    py create_monthly_revenue_by_type.py

Input:  data/online_retail_crm_clean.csv
Output: data/monthly_revenue_by_type.csv

Definition (monthly acquisition-cohort method):
- New: revenue from a customer during their first observed purchase calendar month.
- Returning: revenue from that customer in subsequent calendar months.
- Revenue: Quantity * UnitPrice on valid, identified, positive-price sales.

Only identified-customer revenue is included; this is NOT the same population as
all-sales revenue in MySQL. Original files are not changed.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
source = ROOT / "data" / "online_retail_crm_clean.csv"
target = ROOT / "data" / "monthly_revenue_by_type.csv"

if not source.is_file():
    raise FileNotFoundError(f"找不到输入文件：{source}")

df = pd.read_csv(
    source,
    encoding="utf-8-sig",
    dtype={"CustomerID": "string", "InvoiceNo": "string"},
    low_memory=False,
)
required = {"CustomerID", "InvoiceNo", "InvoiceDate", "Quantity", "UnitPrice"}
missing = required.difference(df.columns)
if missing:
    raise ValueError(f"输入 CSV 缺少字段：{sorted(missing)}")

df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
df["CustomerID"] = df["CustomerID"].str.strip().str.replace(r"\.0$", "", regex=True)
df["InvoiceNo"] = df["InvoiceNo"].str.strip()

valid = (
    df["CustomerID"].notna()
    & (df["CustomerID"] != "")
    & df["InvoiceNo"].notna()
    & (df["InvoiceNo"] != "")
    & df["InvoiceDate"].notna()
    & (df["Quantity"] > 0)
    & (df["UnitPrice"] > 0)
    & ~df["InvoiceNo"].str.upper().str.startswith("C", na=False)
)
valid_rows = int(valid.sum())
df = df.loc[valid].copy()
if df.empty:
    raise ValueError("没有符合条件的可识别客户销售记录，请检查输入 CSV。")

# Consistent with the cohort script: month of first observed valid purchase.
df["PurchaseMonth"] = df["InvoiceDate"].dt.to_period("M")
df["FirstMonth"] = df.groupby("CustomerID")["PurchaseMonth"].transform("min")
df["CustomerType"] = df["PurchaseMonth"].eq(df["FirstMonth"]).map(
    {True: "New", False: "Returning"}
)
df["Revenue"] = df["Quantity"] * df["UnitPrice"]

monthly = (
    df.groupby(["PurchaseMonth", "CustomerType"], observed=True)["Revenue"]
    .sum()
    .unstack(fill_value=0)
    .reindex(columns=["New", "Returning"], fill_value=0)
    .sort_index()
)
# Power Query expects a 'date' column rather than a month string.
monthly.insert(0, "InvoiceDate", monthly.index.to_timestamp().strftime("%Y-%m-%d"))
monthly = monthly.reset_index(drop=True)
monthly[["New", "Returning"]] = monthly[["New", "Returning"]].round(2)
monthly.to_csv(target, index=False, encoding="utf-8-sig")

print(f"生成成功：{target}")
print(f"有效交易记录：{valid_rows:,}")
print(f"可识别客户：{df['CustomerID'].nunique():,}")
print(f"月份数：{len(monthly)}")
print(f"New 总收入：{monthly['New'].sum():,.2f}")
print(f"Returning 总收入：{monthly['Returning'].sum():,.2f}")
print(f"合计收入：{(monthly['New'] + monthly['Returning']).sum():,.2f}")
print("注意：此金额仅覆盖可识别客户，可能不同于 MySQL 全部销售额。")
print("前5行：")
print(monthly.head().to_string(index=False))
