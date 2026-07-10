"""05. 選股組合問題：預算內最大化預期報酬（MILP）

注意：股票名稱、股價、預期報酬率全部是虛構的示範資料。
"""
import pulp

# ---------- 資料（虛構示範資料） ----------
# 股票: (產業, 股價, 預期年報酬率)
stocks = {
    "晶鑫半導體": ("半導體", 580, 0.12),
    "宏達電子":   ("電子",   95,  0.09),
    "富安金控":   ("金融",   28,  0.06),
    "泰昌銀行":   ("金融",   45,  0.07),
    "藍海航運":   ("航運",   120, 0.15),
    "綠能風電":   ("綠能",   65,  0.10),
    "康健生技":   ("生技",   210, 0.11),
    "好食食品":   ("食品",   55,  0.05),
    "雲端資服":   ("資訊",   340, 0.13),
    "大城鋼鐵":   ("鋼鐵",   32,  0.04),
}
sector = {s: v[0] for s, v in stocks.items()}
cost = {s: v[1] * 1000 for s, v in stocks.items()}   # 一張的成本
ret = {s: v[2] for s, v in stocks.items()}
sectors = sorted(set(sector.values()))

BUDGET = 1_000_000
STOCK_CAP = 0.25 * BUDGET    # 單檔上限
SECTOR_CAP = 0.40 * BUDGET   # 產業上限
MIN_POSITION = 80_000        # 有選就至少投入
MIN_STOCKS = 5               # 至少持有檔數

# ---------- 建模 ----------
prob = pulp.LpProblem("stock_portfolio", pulp.LpMaximize)

# 決策變數：n[s] = 買幾張；y[s] = 是否持有（0/1 輔助變數）
n = pulp.LpVariable.dicts("lots", stocks, lowBound=0, cat=pulp.LpInteger)
y = pulp.LpVariable.dicts("pick", stocks, cat=pulp.LpBinary)

# 目標式：預期年報酬金額最大化
prob += pulp.lpSum(ret[s] * cost[s] * n[s] for s in stocks), "預期年報酬"

# 預算限制
prob += pulp.lpSum(cost[s] * n[s] for s in stocks) <= BUDGET, "預算"

# 單檔上限
for s in stocks:
    prob += cost[s] * n[s] <= STOCK_CAP, f"單檔上限_{s}"

# 產業上限
for g in sectors:
    prob += pulp.lpSum(cost[s] * n[s] for s in stocks
                       if sector[s] == g) <= SECTOR_CAP, f"產業上限_{g}"

# 至少持有 MIN_STOCKS 檔
prob += pulp.lpSum(y[s] for s in stocks) >= MIN_STOCKS, "最少檔數"

# 連動限制：沒選不能買（M = 單檔上限內最多能買的張數，自然上界）
for s in stocks:
    max_lots = int(STOCK_CAP // cost[s])
    prob += n[s] <= max_lots * y[s], f"沒選不能買_{s}"
    prob += cost[s] * n[s] >= MIN_POSITION * y[s], f"最低投入_{s}"

# ---------- 求解 ----------
prob.solve(pulp.PULP_CBC_CMD(msg=0))
assert pulp.LpStatus[prob.status] == "Optimal", pulp.LpStatus[prob.status]

# ---------- 結果 ----------
invested = sum(cost[s] * n[s].value() for s in stocks)
print("=== 最佳投資組合（虛構資料示範） ===")
print(f"{'股票':<8}{'產業':<6}{'張數':>4}{'投入金額':>12}{'佔資金':>8}{'預期年報酬':>12}")
for s in stocks:
    lots = round(n[s].value())
    if lots > 0:
        amt = cost[s] * lots
        print(f"{s:<8}{sector[s]:<6}{lots:>4}{amt:>12,.0f}"
              f"{amt / BUDGET:>7.1%}{ret[s] * amt:>12,.0f}")

print(f"\n  投入資金: {invested:,.0f} / {BUDGET:,}（剩餘現金 {BUDGET - invested:,.0f}）")
print(f"  預期年報酬: {pulp.value(prob.objective):,.0f} 元"
      f"（報酬率 {pulp.value(prob.objective) / BUDGET:.2%}）")

print("\n=== 產業曝險 ===")
for g in sectors:
    amt = sum(cost[s] * n[s].value() for s in stocks if sector[s] == g)
    if amt > 0:
        print(f"  {g}: {amt:,.0f}（{amt / BUDGET:.1%}，上限 40%）")
