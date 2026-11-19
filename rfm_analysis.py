
import pandas as pd

# 1. 读取清洗后的 CRM 数据
df = pd.read_csv(
    "data/online_retail_crm_clean.csv",
    parse_dates=["InvoiceDate"],
    dtype={
        "InvoiceNo": str,
        "StockCode": str
    }
)

# 2. 计算每条商品明细的销售金额
df["Sales"] = df["Quantity"] * df["UnitPrice"]

# 3. 设置 RFM 分析基准日期
# 使用数据中最后一天的下一天
snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

# 4. 按客户汇总
rfm = df.groupby("CustomerID").agg(
    Recency=(
        "InvoiceDate",
        lambda x: (snapshot_date - x.max()).days
    ),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("Sales", "sum")
)

# 5. 查看结果
print("RFM 数据规模：", rfm.shape)

print("\nRFM 前5位客户：")
print(rfm.head())

print("\nRFM 描述性统计：")
print(rfm.describe())

print("\n分析基准日期：", snapshot_date)

# 6. 保存客户级数据
rfm.to_csv(
    "data/rfm_customer_summary.csv",
    encoding="utf-8-sig"
)

print("\nRFM 客户汇总数据生成成功！")
