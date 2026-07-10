"""02. 飲食問題：便利商店最低花費菜單（整數規劃）"""
import pulp

# ---------- 資料（示範用虛構數字，非真實商品標示） ----------
# 每份: (價格, 熱量kcal, 蛋白質g, 脂肪g, 鈉mg)
foods = {
    "茶葉蛋":     (13, 75, 7, 5, 350),
    "御飯糰":     (33, 220, 5, 3, 450),
    "即食雞胸肉": (65, 130, 25, 2, 500),
    "生菜沙拉":   (65, 80, 3, 4, 200),
    "無糖豆漿":   (25, 90, 7, 3, 60),
    "香蕉":       (20, 100, 1, 0, 1),
    "優格":       (40, 150, 5, 4, 80),
    "全麥吐司":   (45, 260, 9, 4, 380),
}
price   = {f: v[0] for f, v in foods.items()}
kcal    = {f: v[1] for f, v in foods.items()}
protein = {f: v[2] for f, v in foods.items()}
fat     = {f: v[3] for f, v in foods.items()}
sodium  = {f: v[4] for f, v in foods.items()}

# ---------- 建模 ----------
prob = pulp.LpProblem("diet_problem", pulp.LpMinimize)

# 決策變數：每種食品買幾份（整數，最多 4 份避免怪解）
x = pulp.LpVariable.dicts("servings", foods, lowBound=0, upBound=4,
                          cat=pulp.LpInteger)

# 目標式：花費最小化
prob += pulp.lpSum(price[f] * x[f] for f in foods), "總花費"

# 限制式：營養需求
prob += pulp.lpSum(kcal[f] * x[f] for f in foods) >= 1800, "熱量下限"
prob += pulp.lpSum(kcal[f] * x[f] for f in foods) <= 2400, "熱量上限"
prob += pulp.lpSum(protein[f] * x[f] for f in foods) >= 75, "蛋白質下限"
prob += pulp.lpSum(fat[f] * x[f] for f in foods) <= 70, "脂肪上限"
prob += pulp.lpSum(sodium[f] * x[f] for f in foods) <= 2400, "鈉上限"

# ---------- 求解 ----------
prob.solve(pulp.PULP_CBC_CMD(msg=0))
assert pulp.LpStatus[prob.status] == "Optimal", pulp.LpStatus[prob.status]

# ---------- 結果 ----------
print("=== 最便宜的一日菜單 ===")
for f in foods:
    n = round(x[f].value())
    if n > 0:
        print(f"  {f} x {n}（{price[f] * n} 元）")
print(f"  總花費: {pulp.value(prob.objective):,.0f} 元")

total = lambda d: sum(d[f] * x[f].value() for f in foods)
print("\n=== 營養達成狀況 ===")
print(f"  熱量:   {total(kcal):,.0f} kcal（需求 1800~2400）")
print(f"  蛋白質: {total(protein):,.0f} g（≥ 75）")
print(f"  脂肪:   {total(fat):,.0f} g（≤ 70）")
print(f"  鈉:     {total(sodium):,.0f} mg（≤ 2400）")
