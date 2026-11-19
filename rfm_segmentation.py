
import pandas as pd

# =====================================
# 1. 读取 RFM 评分数据
# =====================================

rfm = pd.read_csv("data/rfm_scored.csv")

print("原始客户数量：", len(rfm))


# =====================================
# 2. 根据 RFM 分数划分客户群体
# =====================================

def classify_customer(row):

    r = row["R_Score"]
    f = row["F_Score"]
    m = row["M_Score"]

    # 历史高消费，但近期不活跃
    if r <= 2 and m >= 4:
        return "历史高消费沉睡客户"

    # 近期活跃，购买频繁，消费金额高
    elif r >= 4 and f >= 4 and m >= 4:
        return "核心高价值客户"

    # 近期活跃，消费金额较高，但频次偏低
    elif r >= 4 and m >= 4 and f <= 3:
        return "高潜力客户"

    # 有一定购买频次且近期仍较活跃
    elif r >= 3 and f >= 3:
        return "活跃复购客户"

    # 最近购买过，但历史消费次数较少
    elif r >= 4 and f <= 2:
        return "近期低频客户"

    # 长时间没有购买
    elif r <= 2:
        return "一般沉睡客户"

    else:
        return "一般维护客户"


# 给每位客户分配一个标签
rfm["Segment"] = rfm.apply(
    classify_customer,
    axis=1
)


# =====================================
# 3. 按客户群体汇总
# =====================================

summary = rfm.groupby(
    "Segment", as_index=False
).agg(
    Customers=("CustomerID", "nunique"),
    Total_Monetary=("Monetary", "sum"),
    Avg_Recency=("Recency", "mean"),
    Avg_Frequency=("Frequency", "mean")
)


# =====================================
# 4. 计算客户占比和消费金额贡献
# =====================================

summary["Customer_Pct"] = (
    summary["Customers"] / len(rfm) * 100
)

summary["Revenue_Pct"] = (
    summary["Total_Monetary"]
    / rfm["Monetary"].sum() * 100
)

# 按累计消费金额贡献降序排列
summary = summary.sort_values(
    "Total_Monetary",
    ascending=False
)


# =====================================
# 5. 验证分层结果
# =====================================

assert rfm["Segment"].notna().all()

assert summary["Customers"].sum() == len(rfm)

assert abs(
    summary["Total_Monetary"].sum()
    - rfm["Monetary"].sum()
) < 0.01


# =====================================
# 6. 查看分析结果
# =====================================

print("\n【客户分层结果】")
print(summary.round(2).to_string(index=False))

print("\n客户总数：", summary["Customers"].sum())

print(
    "累计消费金额：",
    round(summary["Total_Monetary"].sum(), 2)
)


# =====================================
# 7. 保存结果
# =====================================

rfm.to_csv(
    "data/rfm_segmented.csv",
    index=False,
    encoding="utf-8-sig"
)

summary.to_csv(
    "data/rfm_segment_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n客户分层完成！")
print("已保存：data/rfm_segmented.csv")
print("已保存：data/rfm_segment_summary.csv")
