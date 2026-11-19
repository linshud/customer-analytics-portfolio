
import pandas as pd

# 1. 读取 RFM 汇总结果
rfm = pd.read_csv("data/rfm_customer_summary.csv")

# 将客户编号转换为整数
rfm["CustomerID"] = rfm["CustomerID"].astype(int)

# 2. R 评分：越近期购买，分数越高
rfm["R_Score"] = pd.cut(
    rfm["Recency"],
    bins=[0, 30, 60, 90, 180, float("inf")],
    labels=[5, 4, 3, 2, 1]
).astype(int)

# 3. F 评分：购买次数越多，分数越高
rfm["F_Score"] = pd.cut(
    rfm["Frequency"],
    bins=[0, 1, 2, 4, 9, float("inf")],
    labels=[1, 2, 3, 4, 5]
).astype(int)

# 4. M 评分：按累计消费金额五分位评分
rfm["M_Score"] = pd.qcut(
    rfm["Monetary"],
    q=5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

# 5. 计算总分
rfm["RFM_Score"] = (
    rfm["R_Score"]
    + rfm["F_Score"]
    + rfm["M_Score"]
)

# 6. 显示前10位客户
print("\n【RFM 评分结果】")
print(rfm.head(10).to_string(index=False))

# 7. 统计各评分的分布
print("\n【R 评分分布】")
print(rfm["R_Score"].value_counts().sort_index())

print("\n【F 评分分布】")
print(rfm["F_Score"].value_counts().sort_index())

print("\n【M 评分分布】")
print(rfm["M_Score"].value_counts().sort_index())

# 8. 检查评分范围
assert rfm["RFM_Score"].between(3, 15).all()

# 9. 保存评分数据
rfm.to_csv(
    "data/rfm_scored.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nRFM 评分成功！")
print("客户数量：", len(rfm))
print("文件已保存：data/rfm_scored.csv")
