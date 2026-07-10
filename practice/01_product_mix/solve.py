"""01. 生產組合問題：手搖飲店每日產量規劃（純 LP）"""
import pulp

# ---------- 資料（示範用虛構數字） ----------
products = ["珍珠奶茶", "水果茶", "鮮奶拿鐵"]
profit = {"珍珠奶茶": 35, "水果茶": 45, "鮮奶拿鐵": 40}  # 元/杯

# 每杯消耗的資源
usage = {
    "工時":  {"珍珠奶茶": 3,   "水果茶": 5,  "鮮奶拿鐵": 4},    # 分鐘
    "珍珠":  {"珍珠奶茶": 50,  "水果茶": 0,  "鮮奶拿鐵": 0},    # 克
    "茶葉":  {"珍珠奶茶": 8,   "水果茶": 10, "鮮奶拿鐵": 6},    # 克
    "鮮奶":  {"珍珠奶茶": 150, "水果茶": 0,  "鮮奶拿鐵": 200},  # 毫升
}
capacity = {"工時": 960, "珍珠": 6000, "茶葉": 1500, "鮮奶": 30000}

# ---------- 建模 ----------
prob = pulp.LpProblem("product_mix", pulp.LpMaximize)

# 決策變數：每種飲品做幾杯（連續值，入門先不管整數）
x = pulp.LpVariable.dicts("cups", products, lowBound=0)

# 目標式：利潤最大化
prob += pulp.lpSum(profit[p] * x[p] for p in products), "總利潤"

# 限制式：每項資源不能超過每日上限
for res, cap in capacity.items():
    prob += pulp.lpSum(usage[res][p] * x[p] for p in products) <= cap, res

# ---------- 求解 ----------
prob.solve(pulp.PULP_CBC_CMD(msg=0))
assert pulp.LpStatus[prob.status] == "Optimal", pulp.LpStatus[prob.status]

# ---------- 結果 ----------
print("=== 最佳生產計畫 ===")
for p in products:
    print(f"  {p}: {x[p].value():.1f} 杯")
print(f"  總利潤: {pulp.value(prob.objective):,.0f} 元")

print("\n=== 資源使用與影子價格 ===")
print("（影子價格 = 該資源多 1 單位，利潤可增加多少；0 代表該資源沒用完）")
for res, constraint in prob.constraints.items():
    slack = round(constraint.slack, 6) + 0  # 四捨五入再 +0，消除 -0.0 的顯示
    pi = round(constraint.pi, 6) + 0
    used = capacity[res] - slack
    print(f"  {res}: 用了 {used:,.0f} / {capacity[res]:,}"
          f"（剩 {slack:,.0f}），影子價格 = {pi:.2f}")
