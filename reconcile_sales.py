
import pandas as pd
from pathlib import Path

DATA = Path("data")

files = [
    "online_retail_sales_clean.csv",
    "online_retail_crm_clean.csv",
    "unidentified_customer_sales.csv",
    "rfm_customer_summary.csv",
    "rfm_scored.csv",
    "rfm_segmented.csv",
    "rfm_segment_summary.csv"
]


# Safeguard: do not overwrite the verified reconciliation report when
# the lightweight GitHub portfolio omits source transaction datasets.
missing_inputs = [name for name in files if not (DATA / name).is_file()]
if missing_inputs:
    raise FileNotFoundError(
        "无法生成完整核对报告，以下输入文件不存在：\n  "
        + "\n  ".join(missing_inputs)
        + "\n请在包含完整交易数据的原项目中运行，已保存的核对报告不会被覆盖。"
    )

results = {}

for filename in files:

    path = DATA / filename

    print("\n" + "=" * 55)
    print("正在检查：", filename)

    if not path.exists():
        print("文件不存在，跳过")
        continue

    df = pd.read_csv(path, low_memory=False)

    result = {
        "文件": filename,
        "记录数": len(df)
    }

    # 计算交易金额
    if "Quantity" in df.columns and "UnitPrice" in df.columns:

        quantity = pd.to_numeric(
            df["Quantity"], errors="coerce"
        )

        price = pd.to_numeric(
            df["UnitPrice"], errors="coerce"
        )

        df["LineRevenue"] = quantity * price

        result["销售金额"] = df["LineRevenue"].sum()

        result["缺失客户ID行数"] = (
            df["CustomerID"].isna().sum()
            if "CustomerID" in df.columns else None
        )

        result["负数数量行数"] = (quantity < 0).sum()

        result["取消订单行数"] = (
            df["InvoiceNo"].astype(str)
            .str.startswith("C").sum()
        )

        result["完全重复行数"] = df.duplicated().sum()

    # RFM 客户汇总金额
    if "Monetary" in df.columns:

        result["RFM金额"] = pd.to_numeric(
            df["Monetary"], errors="coerce"
        ).sum()

    # 客户分层汇总金额
    if "Total_Monetary" in df.columns:

        result["RFM金额"] = pd.to_numeric(
            df["Total_Monetary"], errors="coerce"
        ).sum()

    results[filename] = result

    for key, value in result.items():
        print(f"{key}：{value}")


# =================================
# 核对销售数据与客户数据
# =================================

print("\n\n========== 数据核对结果 ==========")

sales = results.get("online_retail_sales_clean.csv", {})
crm = results.get("online_retail_crm_clean.csv", {})
unknown = results.get("unidentified_customer_sales.csv", {})

if sales and crm and unknown:

    row_diff = (
        sales["记录数"]
        - crm["记录数"]
        - unknown["记录数"]
    )

    amount_diff = (
        sales["销售金额"]
        - crm["销售金额"]
        - unknown["销售金额"]
    )

    print("\n【记录数核对】")
    print("销售数据：", sales["记录数"])
    print("CRM数据：", crm["记录数"])
    print("未识别客户数据：", unknown["记录数"])
    print("行数差额：", row_diff)

    print("\n【销售金额核对】")
    print("销售数据金额：", round(sales["销售金额"], 2))
    print("CRM数据金额：", round(crm["销售金额"], 2))
    print("未识别客户金额：", round(unknown["销售金额"], 2))
    print("金额差额：", round(amount_diff, 2))


# =================================
# 核对 RFM 金额
# =================================

print("\n【CRM与RFM金额核对】")

for filename in [
    "rfm_customer_summary.csv",
    "rfm_scored.csv",
    "rfm_segmented.csv",
    "rfm_segment_summary.csv"
]:

    if filename in results:

        amount = results[filename].get("RFM金额")

        if amount is not None:
            print(filename, "：", round(amount, 2))


# =================================
# 保存核对报告
# =================================

report = pd.DataFrame(results.values())

report.to_csv(
    DATA / "reconciliation_report.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n核对完成！")
print("报告已保存：data/reconciliation_report.csv")
