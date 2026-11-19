"""Generate the 14-column monthly cohort-retention CSV expected by the existing Power BI query.

Place this script in the project root, next to the data/ folder, and run:
    py create_cohort_retention.py

Input:  data/online_retail_crm_clean.csv
Output: data/cohort_retention.csv

Retention definition: distinct customers buying in a specific calendar month / distinct
customers first observed purchasing in their cohort month * 100.
Months beyond the data's observation window are blank (not falsely set to zero).
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
source = ROOT / "data" / "online_retail_crm_clean.csv"
target = ROOT / "data" / "cohort_retention.csv"

if not source.is_file():
    raise FileNotFoundError(f"找不到客户交易文件：{source}")

df = pd.read_csv(
    source,
    dtype={"CustomerID": "string", "InvoiceNo": "string"},
    low_memory=False,
    encoding="utf-8-sig",
)
required = {"CustomerID", "InvoiceNo", "InvoiceDate", "Quantity", "UnitPrice"}
missing = required.difference(df.columns)
if missing:
    raise ValueError(f"CSV 缺少字段：{sorted(missing)}")

df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
df["CustomerID"] = df["CustomerID"].str.strip().str.replace(r"\.0$", "", regex=True)
df["InvoiceNo"] = df["InvoiceNo"].str.strip()
df = df.dropna(subset=["CustomerID", "InvoiceNo", "InvoiceDate"])
df = df[
    (df["CustomerID"] != "")
    & (df["Quantity"] > 0)
    & (df["UnitPrice"] > 0)
    & (~df["InvoiceNo"].str.upper().str.startswith("C", na=False))
].copy()
if df.empty:
    raise ValueError("筛选后没有有效客户交易记录，请检查数据文件及字段。")

# Earliest observed purchase month determines each customer's cohort.
df["PurchaseMonth"] = df["InvoiceDate"].dt.to_period("M")
df["CohortMonth"] = df.groupby("CustomerID")["PurchaseMonth"].transform("min")
df["MonthsSinceFirst"] = (
    (df["PurchaseMonth"].dt.year - df["CohortMonth"].dt.year) * 12
    + (df["PurchaseMonth"].dt.month - df["CohortMonth"].dt.month)
)

cohort_sizes = df.groupby("CohortMonth")["CustomerID"].nunique()
monthly_customers = (
    df.groupby(["CohortMonth", "MonthsSinceFirst"])["CustomerID"]
    .nunique()
    .unstack()
    .reindex(columns=range(13))
)
retention = monthly_customers.div(cohort_sizes, axis=0).mul(100)

# Observed but empty months get 0%; unobserved future months stay blank.
last_month = df["PurchaseMonth"].max()
for cohort in retention.index:
    latest_observable_age = min(
        12, (last_month.year - cohort.year) * 12 + (last_month.month - cohort.month)
    )
    for age in range(latest_observable_age + 1):
        if pd.isna(retention.loc[cohort, age]):
            retention.loc[cohort, age] = 0.0

retention = retention.round(2)
retention.columns = [str(col) for col in retention.columns]
retention.insert(0, "CohortMonth", retention.index.astype(str))
retention = retention.reset_index(drop=True)
# Month 0 should be an integer so the existing Power Query Int64 conversion works.
retention["0"] = retention["0"].astype("Int64")
retention.to_csv(target, index=False, encoding="utf-8", na_rep="")

print(f"生成成功：{target}")
print(f"有效客户数：{df['CustomerID'].nunique():,}")
print(f"Cohort 月份数：{len(retention)}")
print("输出列：", list(retention.columns))
print(retention.head(3).to_string(index=False))
