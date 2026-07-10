"""03. 員工排班問題：連上 5 休 2 的最少人力配置（覆蓋式整數規劃）"""
import pulp

# ---------- 資料（示範用虛構數字） ----------
days = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
demand = [4, 3, 4, 5, 7, 9, 6]  # 每天需要的最少人數

WORK = 5  # 每種班型連續上班天數

# ---------- 建模 ----------
prob = pulp.LpProblem("staff_scheduling", pulp.LpMinimize)

# 決策變數：x[j] = 從星期 j 開始連上 5 天的班型，雇用幾個人
x = pulp.LpVariable.dicts("shift", range(7), lowBound=0, cat=pulp.LpInteger)

# 目標式：總雇用人數最小化
prob += pulp.lpSum(x[j] for j in range(7)), "總人數"

# 限制式（覆蓋限制）：每天 d 有上班的班型人數加總 >= 當天需求
# 班型 j 的上班日是 j, j+1, ..., j+4 (mod 7)
# 反過來說：第 d 天有上班的班型是 j = d, d-1, ..., d-4 (mod 7)
for d in range(7):
    covering = [(d - k) % 7 for k in range(WORK)]
    prob += pulp.lpSum(x[j] for j in covering) >= demand[d], days[d]

# ---------- 求解 ----------
prob.solve(pulp.PULP_CBC_CMD(msg=0))
assert pulp.LpStatus[prob.status] == "Optimal", pulp.LpStatus[prob.status]

# ---------- 結果 ----------
print("=== 各班型雇用人數 ===")
for j in range(7):
    n = round(x[j].value())
    if n > 0:
        work_days = "、".join(days[(j + k) % 7] for k in range(WORK))
        print(f"  {days[j]}起連上5天（{work_days}）: {n} 人")
print(f"  總雇用人數: {pulp.value(prob.objective):.0f} 人")

print("\n=== 每日人力 vs 需求 ===")
for d in range(7):
    staffed = sum(round(x[(d - k) % 7].value()) for k in range(WORK))
    extra = f"（過剩 {staffed - demand[d]}）" if staffed > demand[d] else ""
    print(f"  {days[d]}: 上班 {staffed} 人 / 需求 {demand[d]} 人 {extra}")
