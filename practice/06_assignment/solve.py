"""06. 指派問題：工程師與功能的一對一分工（0/1 整數規劃）"""
import pulp

# ---------- 資料（示範用虛構數字） ----------
people = ["阿明", "小美", "大雄", "靜香"]
tasks = ["會員系統", "支付系統", "報表模組", "通知服務"]

# 預估工時（小時）；None 代表不可指派
hours = {
    "阿明": {"會員系統": 12, "支付系統": 18, "報表模組": 8,  "通知服務": 14},
    "小美": {"會員系統": 10, "支付系統": None, "報表模組": 14, "通知服務": 6},
    "大雄": {"會員系統": 15, "支付系統": 12, "報表模組": 16, "通知服務": 11},
    "靜香": {"會員系統": 9,  "支付系統": 16, "報表模組": 12, "通知服務": 13},
}

# ---------- 建模 ----------
prob = pulp.LpProblem("assignment", pulp.LpMinimize)

# 決策變數：x[p][t] = 工程師 p 是否負責功能 t
x = pulp.LpVariable.dicts("assign", (people, tasks), cat=pulp.LpBinary)

# 目標式：總工時最小化（不可指派的組合不計入目標式）
prob += pulp.lpSum(hours[p][t] * x[p][t]
                   for p in people for t in tasks
                   if hours[p][t] is not None), "總工時"

# 限制式：每位工程師剛好負責一個功能
for p in people:
    prob += pulp.lpSum(x[p][t] for t in tasks) == 1, f"一人一事_{p}"

# 限制式：每個功能剛好一個人負責
for t in tasks:
    prob += pulp.lpSum(x[p][t] for p in people) == 1, f"一事一人_{t}"

# 限制式：不可行的組合直接固定為 0
for p in people:
    for t in tasks:
        if hours[p][t] is None:
            prob += x[p][t] == 0, f"不可指派_{p}_{t}"

# ---------- 求解 ----------
prob.solve(pulp.PULP_CBC_CMD(msg=0))
assert pulp.LpStatus[prob.status] == "Optimal", pulp.LpStatus[prob.status]

# ---------- 結果 ----------
print("=== 最佳分工 ===")
for p in people:
    for t in tasks:
        if x[p][t].value() > 0.5:
            print(f"  {p} → {t}（{hours[p][t]} 小時）")
print(f"  總工時: {pulp.value(prob.objective):.0f} 小時")
