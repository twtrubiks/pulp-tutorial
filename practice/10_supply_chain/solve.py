"""10. 供應鏈網路：工廠 → DC → 客戶 兩段運輸（MILP，流量守恆）"""
import pulp

# ---------- 資料（示範用虛構數字） ----------
factories = {"桃園廠": 500, "台中廠": 400, "高雄廠": 600}      # 月產能（件）
dc_capacity = {"北區DC": 800, "中區DC": 700, "南區DC": 600}    # 月容量（件）
dc_fixed = {"北區DC": 60_000, "中區DC": 45_000, "南區DC": 40_000}  # 月固定成本
demand = {"台北": 300, "新竹": 150, "台中": 200, "台南": 150, "高雄": 200}

# 單位運費（元/件）：工廠 → DC
cost_fd = {
    "桃園廠": {"北區DC": 4, "中區DC": 9, "南區DC": 16},
    "台中廠": {"北區DC": 10, "中區DC": 3, "南區DC": 10},
    "高雄廠": {"北區DC": 18, "中區DC": 10, "南區DC": 3},
}
# 單位運費（元/件）：DC → 客戶
cost_dc = {
    "北區DC": {"台北": 3, "新竹": 6, "台中": 12, "台南": 20, "高雄": 24},
    "中區DC": {"台北": 12, "新竹": 7, "台中": 3, "台南": 10, "高雄": 14},
    "南區DC": {"台北": 22, "新竹": 16, "台中": 11, "台南": 4, "高雄": 3},
}

# ---------- 建模 ----------
prob = pulp.LpProblem("supply_chain", pulp.LpMinimize)

# 決策變數：f[i][j] = 工廠 i → DC j 件數；g[j][k] = DC j → 客戶 k 件數
#           y[j] = 是否啟用 DC j
f = pulp.LpVariable.dicts("factory_dc", (factories, dc_capacity), lowBound=0)
g = pulp.LpVariable.dicts("dc_customer", (dc_capacity, demand), lowBound=0)
y = pulp.LpVariable.dicts("open", dc_capacity, cat=pulp.LpBinary)

# 目標式：固定成本 + 兩段運費 最小化
prob += (pulp.lpSum(dc_fixed[j] * y[j] for j in dc_capacity)
         + pulp.lpSum(cost_fd[i][j] * f[i][j]
                      for i in factories for j in dc_capacity)
         + pulp.lpSum(cost_dc[j][k] * g[j][k]
                      for j in dc_capacity for k in demand)), "總成本"

# 限制式：工廠產能
for i in factories:
    prob += pulp.lpSum(f[i][j] for j in dc_capacity) <= factories[i], f"產能_{i}"

# 限制式：DC 容量 + 連動（沒啟用的 DC 容量視為 0）
for j in dc_capacity:
    prob += (pulp.lpSum(f[i][j] for i in factories)
             <= dc_capacity[j] * y[j]), f"容量_{j}"

# 限制式：流量守恆（DC 進多少就出多少）
for j in dc_capacity:
    prob += (pulp.lpSum(f[i][j] for i in factories)
             == pulp.lpSum(g[j][k] for k in demand)), f"流量守恆_{j}"

# 限制式：客戶需求剛好滿足
for k in demand:
    prob += pulp.lpSum(g[j][k] for j in dc_capacity) == demand[k], f"需求_{k}"

# ---------- 求解 ----------
prob.solve(pulp.PULP_CBC_CMD(msg=0))
assert pulp.LpStatus[prob.status] == "Optimal", pulp.LpStatus[prob.status]

# ---------- 結果 ----------
print("=== DC 啟用決策 ===")
fixed_cost = 0
for j in dc_capacity:
    if y[j].value() > 0.5:
        inflow = sum(f[i][j].value() for i in factories)
        fixed_cost += dc_fixed[j]
        print(f"  啟用 {j}（固定成本 {dc_fixed[j]:,}，"
              f"流量 {inflow:,.0f}/{dc_capacity[j]:,} 件）")
    else:
        print(f"  不啟用 {j}")

print("\n=== 第一段：工廠 → DC（件） ===")
fd_cost = 0
for i in factories:
    for j in dc_capacity:
        qty = f[i][j].value()
        if qty > 0.5:
            fd_cost += cost_fd[i][j] * qty
            print(f"  {i} → {j}: {qty:,.0f}")

print("\n=== 第二段：DC → 客戶（件） ===")
dc_cost = 0
for j in dc_capacity:
    for k in demand:
        qty = g[j][k].value()
        if qty > 0.5:
            dc_cost += cost_dc[j][k] * qty
            print(f"  {j} → {k}: {qty:,.0f}")

print(f"\n  固定成本:     {fixed_cost:>9,.0f} 元")
print(f"  第一段運費:   {fd_cost:>9,.0f} 元")
print(f"  第二段運費:   {dc_cost:>9,.0f} 元")
print(f"  總成本:       {pulp.value(prob.objective):>9,.0f} 元/月")
