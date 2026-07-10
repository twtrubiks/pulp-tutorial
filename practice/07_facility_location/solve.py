"""07. 設施選址問題：開倉決策 + 出貨配送（MILP，固定成本與 big-M）"""
import pulp

# ---------- 資料（示範用虛構數字） ----------
warehouses = ["新北倉", "桃園倉", "台中倉", "高雄倉"]
regions = ["北北基", "桃竹苗", "中彰投", "雲嘉南", "高屏"]

fixed = {"新北倉": 300_000, "桃園倉": 220_000, "台中倉": 180_000, "高雄倉": 200_000}
capacity = {"新北倉": 8000, "桃園倉": 6000, "台中倉": 5000, "高雄倉": 6000}
demand = {"北北基": 4000, "桃竹苗": 2500, "中彰投": 2600, "雲嘉南": 1500, "高屏": 2400}

# 單件運費（元）
ship = {
    "新北倉": {"北北基": 15, "桃竹苗": 25, "中彰投": 45, "雲嘉南": 60, "高屏": 70},
    "桃園倉": {"北北基": 22, "桃竹苗": 12, "中彰投": 35, "雲嘉南": 50, "高屏": 62},
    "台中倉": {"北北基": 45, "桃竹苗": 30, "中彰投": 12, "雲嘉南": 25, "高屏": 40},
    "高雄倉": {"北北基": 70, "桃竹苗": 60, "中彰投": 38, "雲嘉南": 20, "高屏": 10},
}

# ---------- 建模 ----------
prob = pulp.LpProblem("facility_location", pulp.LpMinimize)

# 決策變數：y[w] = 是否開倉；x[w][r] = 倉庫 w 出貨到地區 r 的件數
y = pulp.LpVariable.dicts("open", warehouses, cat=pulp.LpBinary)
x = pulp.LpVariable.dicts("ship", (warehouses, regions), lowBound=0)

# 目標式：固定成本 + 運費 最小化
prob += (pulp.lpSum(fixed[w] * y[w] for w in warehouses)
         + pulp.lpSum(ship[w][r] * x[w][r]
                      for w in warehouses for r in regions)), "總成本"

# 限制式：每個地區需求要剛好滿足
for r in regions:
    prob += pulp.lpSum(x[w][r] for w in warehouses) == demand[r], f"需求_{r}"

# 限制式：容量 + 連動（沒開的倉庫容量視為 0，不能出貨）
for w in warehouses:
    prob += (pulp.lpSum(x[w][r] for r in regions)
             <= capacity[w] * y[w]), f"容量_{w}"

# ---------- 求解 ----------
prob.solve(pulp.PULP_CBC_CMD(msg=0))
assert pulp.LpStatus[prob.status] == "Optimal", pulp.LpStatus[prob.status]

# ---------- 結果 ----------
fixed_cost = sum(fixed[w] * y[w].value() for w in warehouses)
ship_cost = pulp.value(prob.objective) - fixed_cost

print("=== 開倉決策 ===")
for w in warehouses:
    if y[w].value() > 0.5:
        used = sum(x[w][r].value() for r in regions)
        print(f"  開 {w}（固定成本 {fixed[w]:,}，使用 {used:,.0f}/{capacity[w]:,} 件容量）")
    else:
        print(f"  不開 {w}")

print("\n=== 配送計畫（件） ===")
for w in warehouses:
    for r in regions:
        if x[w][r].value() > 0.5:
            print(f"  {w} → {r}: {x[w][r].value():,.0f} 件"
                  f"（運費 {ship[w][r] * x[w][r].value():,.0f} 元）")

print(f"\n  固定成本: {fixed_cost:,.0f} 元")
print(f"  運費:     {ship_cost:,.0f} 元")
print(f"  總成本:   {pulp.value(prob.objective):,.0f} 元/月")
