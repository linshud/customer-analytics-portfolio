
import pandas as pd

# =====================================
# 1. 读取原始数据
# =====================================

df = pd.read_csv(
    "data/online_retail_raw.csv",
    dtype={"InvoiceNo": str, "StockCode": str},
    parse_dates=["InvoiceDate"]
)

print("原始数据量：", len(df))


# =====================================
# 2. 识别并保存完全重复记录
# =====================================

duplicate_mask = df.duplicated(keep="first")

# 保存重复组中的所有记录，方便检查
duplicate_all = df.loc[
    df.duplicated(keep=False)
].copy()

duplicate_all.to_csv(
    "data/duplicate_records.csv",
    index=False,
    encoding="utf-8-sig"
)

# 删除额外重复行
df = df.drop_duplicates(keep="first").copy()

print("删除的重复行数：", duplicate_mask.sum())


# =====================================
# 3. 识别取消订单
# =====================================

is_cancel = df["InvoiceNo"].str.startswith(
    "C", na=False
)


# =====================================
# 4. 筛选正向付费销售记录
# =====================================

valid_sales = (
    (~is_cancel)
    & (df["Quantity"] > 0)
    & (df["UnitPrice"] > 0)
)

sales_clean = df.loc[valid_sales].copy()


# =====================================
# 5. 保存无法识别客户的销售记录
# =====================================

unknown_customer = sales_clean.loc[
    sales_clean["CustomerID"].isna()
].copy()

unknown_customer.to_csv(
    "data/unidentified_customer_sales.csv",
    index=False,
    encoding="utf-8-sig"
)


# =====================================
# 6. 生成 CRM 用户分析数据
# =====================================

crm_clean = sales_clean.loc[
    sales_clean["CustomerID"].notna()
].copy()


# =====================================
# 7. 保存其他非正向销售记录
# =====================================

excluded = df.loc[~valid_sales].copy()

excluded.to_csv(
    "data/excluded_transactions.csv",
    index=False,
    encoding="utf-8-sig"
)


# =====================================
# 8. 输出两个清洗结果
# =====================================

sales_clean.to_csv(
    "data/online_retail_sales_clean.csv",
    index=False,
    encoding="utf-8-sig"
)

crm_clean.to_csv(
    "data/online_retail_crm_clean.csv",
    index=False,
    encoding="utf-8-sig"
)


# =====================================
# 9. 输出清洗报告
# =====================================

print("\n========== 数据清洗报告 ==========")

print("原始记录数：", len(pd.read_csv(
    "data/online_retail_raw.csv"
)))

print("去重后记录数：", len(df))

print("销售分析记录数：", len(sales_clean))

print("CRM 分析记录数：", len(crm_clean))

print("无法识别客户的销售记录：", len(unknown_customer))

print("非正向销售记录：", len(excluded))

print("\n销售金额：",
      (sales_clean["Quantity"] *
       sales_clean["UnitPrice"]).sum())

print("\nCRM 数据客户数量：",
      crm_clean["CustomerID"].nunique())

print("\nCRM 数据订单数量：",
      crm_clean["InvoiceNo"].nunique())

print("\n数据清洗完成！")
