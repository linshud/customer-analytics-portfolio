
import pandas as pd
from pathlib import Path

# 1. 设置文件路径
source = Path("data/Online Retail.xlsx")
target = Path("data/online_retail_raw.csv")

# 2. 检查原始文件是否存在
if not source.exists():
    raise FileNotFoundError(f"找不到原始数据：{source}")

# 3. 读取 Excel
df = pd.read_excel(source)

# 4. 整理字段名称
df.columns = df.columns.astype(str).str.strip()

# 5. 兼容不同的数据集字段名称
rename_map = {
    old: new
    for old, new in {
        "Invoice": "InvoiceNo",
        "Price": "UnitPrice",
        "Customer ID": "CustomerID"
    }.items()
    if old in df.columns and new not in df.columns
}

df = df.rename(columns=rename_map)

# 6. 检查必要字段
required_columns = [
    "InvoiceNo", "StockCode", "Description",
    "Quantity", "InvoiceDate", "UnitPrice",
    "CustomerID", "Country"
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    raise ValueError(f"缺少必要字段：{missing}")

# 7. 输出数据基本信息
print("原始数据行列数：", df.shape)
print("\n字段名称：")
print(df.columns.tolist())

print("\n缺失值统计：")
print(df.isnull().sum())

# 8. 转换为 CSV
df.to_csv(target, index=False, encoding="utf-8-sig")

print("\nExcel 转 CSV 成功！")
print("文件保存位置：", target)
