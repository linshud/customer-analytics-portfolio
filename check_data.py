
import pandas as pd

# 读取刚才转换好的 CSV
df = pd.read_csv(
    "data/online_retail_raw.csv",
    parse_dates=["InvoiceDate"],
    dtype={"InvoiceNo": str, "StockCode": str}
)

print("=" * 50)
print("CRM 数据质量检查报告")
print("=" * 50)

# 1. 数据规模
print("\n【1. 数据基本信息】")
print("数据行列数：", df.shape)
print("客户数量：", df["CustomerID"].nunique())
print("订单数量：", df["InvoiceNo"].nunique())

# 2. 缺失值
print("\n【2. 缺失值检查】")
print(df.isnull().sum())

# 3. 重复值
print("\n【3. 重复记录检查】")
print("重复记录数：", df.duplicated().sum())

# 4. 取消订单
print("\n【4. 取消订单检查】")
cancelled = df["InvoiceNo"].str.startswith(
    "C", na=False
)
print("取消订单明细行数：", cancelled.sum())

# 5. 异常数量
print("\n【5. Quantity 异常检查】")
print("负数数量记录：", (df["Quantity"] < 0).sum())
print("零数量记录：", (df["Quantity"] == 0).sum())

# 6. 异常价格
print("\n【6. UnitPrice 异常检查】")
print("负数价格记录：", (df["UnitPrice"] < 0).sum())
print("零价格记录：", (df["UnitPrice"] == 0).sum())

# 7. 日期范围
print("\n【7. 时间范围】")
print("最早交易：", df["InvoiceDate"].min())
print("最晚交易：", df["InvoiceDate"].max())

print("\n数据质量检查完成！")
