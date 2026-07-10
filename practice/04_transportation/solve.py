"""04. 運輸問題：倉庫到門市的最低運費配送（純 LP）"""
import pulp

# ---------- 資料（示範用虛構數字） ----------
warehouses = ["桃園倉", "彰化倉", "台南倉"]
stores = ["台北門市", "台中門市", "高雄門市", "花蓮門市"]

supply = {"桃園倉": 300, "彰化倉": 400, "台南倉": 300}
demand = {"台北門市": 250, "台中門市": 300, "高雄門市": 350, "花蓮門市": 50}

# 運費（元/箱）
cost = {
    "桃園倉": {"台北門市": 20, "台中門市": 45, "高雄門市": 80, "花蓮門市": 90},
    "彰化倉": {"台北門市": 50, "台中門市": 15, "高雄門市": 40, "花蓮門市": 95},
    "台南倉": {"台北門市": 75, "台中門市": 35, "高雄門市": 15, "花蓮門市": 110},
}

# ---------- 建模 ----------
prob = pulp.LpProblem("transportation", pulp.LpMinimize)

# 決策變數：x[w][s] = 倉庫 w 送到門市 s 的箱數
x = pulp.LpVariable.dicts("ship", (warehouses, stores), lowBound=0)

# 目標式：總運費最小化
prob += pulp.lpSum(cost[w][s] * x[w][s]
                   for w in warehouses for s in stores), "總運費"

# 限制式：倉庫出貨 <= 庫存（供給 > 需求，用不等式）
for w in warehouses:
    prob += pulp.lpSum(x[w][s] for s in stores) <= supply[w], f"供給_{w}"

# 限制式：門市需求要剛好滿足
for s in stores:
    prob += pulp.lpSum(x[w][s] for w in warehouses) == demand[s], f"需求_{s}"

# ---------- 求解 ----------
prob.solve(pulp.PULP_CBC_CMD(msg=0))
assert pulp.LpStatus[prob.status] == "Optimal", pulp.LpStatus[prob.status]

# ---------- 結果 ----------
print("=== 最佳配送計畫（箱） ===")
header = "        " + "".join(f"{s:>10}" for s in stores)
print(header)
for w in warehouses:
    row = "".join(f"{x[w][s].value():>12.0f}" for s in stores)
    shipped = sum(x[w][s].value() for s in stores)
    print(f"  {w}{row}   （出貨 {shipped:.0f}/{supply[w]}）")
print(f"\n  總運費: {pulp.value(prob.objective):,.0f} 元")
