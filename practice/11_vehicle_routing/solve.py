"""11. 車輛路徑問題：cluster-first route-second（指派 + TSP/MTZ）"""
import math

import pulp

# ---------- 資料（示範用虛構數字） ----------
DEPOT = "物流站"
customers = {  # {客戶: (x, y, 需求)}
    "A": (2, 4, 10), "B": (5, 2, 8), "C": (7, 8, 12),
    "D": (3, 7, 6), "E": (8, 3, 9), "F": (6, 6, 7),
}
vehicles = ["車1", "車2"]
CAPACITY = 30

xy = {DEPOT: (0, 0), **{c: (x, y) for c, (x, y, _) in customers.items()}}


def dist(p, q):
    return math.hypot(xy[p][0] - xy[q][0], xy[p][1] - xy[q][1])


# ---------- 第一階段：分群（cluster-first） ----------
# 種子 = 相距最遠的兩個客戶。
# 注意：不能用「站點到客戶的往返距離」當指派目標——每個客戶都要被指派，
# 那個總和是常數，對決策毫無鑑別力（見 README）。
seed_a, seed_b = max(
    ((c1, c2) for c1 in customers for c2 in customers if c1 < c2),
    key=lambda pair: dist(pair[0], pair[1]))
seeds = {vehicles[0]: seed_a, vehicles[1]: seed_b}
print(f"=== 第一階段：分群（種子：{seed_a}、{seed_b}） ===")

cluster = pulp.LpProblem("clustering", pulp.LpMinimize)

# 決策變數：a[(v, c)] = 客戶 c 是否由車 v 服務
a = pulp.LpVariable.dicts(
    "assign", ((v, c) for v in vehicles for c in customers), cat=pulp.LpBinary)

# 目標式：每個客戶離自己車隊的種子越近越好
cluster += pulp.lpSum(dist(c, seeds[v]) * a[(v, c)]
                      for v in vehicles for c in customers), "離種子距離"

for c in customers:
    cluster += pulp.lpSum(a[(v, c)] for v in vehicles) == 1, f"服務_{c}"
for v in vehicles:
    cluster += (pulp.lpSum(customers[c][2] * a[(v, c)] for c in customers)
                <= CAPACITY), f"載重_{v}"
    cluster += a[(v, seeds[v])] == 1, f"種子_{v}"

cluster.solve(pulp.PULP_CBC_CMD(msg=0))
assert pulp.LpStatus[cluster.status] == "Optimal", pulp.LpStatus[cluster.status]

groups = {v: [c for c in customers if a[(v, c)].value() > 0.5] for v in vehicles}
for v in vehicles:
    load = sum(customers[c][2] for c in groups[v])
    print(f"  {v}: {', '.join(groups[v])}（載重 {load}/{CAPACITY}）")


# ---------- 第二階段：排路線（route-second，TSP + MTZ） ----------
def solve_tsp(stops):
    """stops：含物流站的節點列表。回傳（依序路線, 總距離）。"""
    n = len(stops)
    arcs = [(i, j) for i in stops for j in stops if i != j]

    tsp = pulp.LpProblem("tsp", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("arc", arcs, cat=pulp.LpBinary)
    # MTZ 順序變數（不含站點）
    u = pulp.LpVariable.dicts("order", [s for s in stops if s != DEPOT],
                              lowBound=1, upBound=n - 1, cat=pulp.LpInteger)

    tsp += pulp.lpSum(dist(i, j) * x[(i, j)] for i, j in arcs), "總距離"

    for i in stops:  # 每點出一次、進一次
        tsp += pulp.lpSum(x[(i, j)] for j in stops if j != i) == 1
        tsp += pulp.lpSum(x[(j, i)] for j in stops if j != i) == 1
    # MTZ 子迴圈消除：走 i→j 就強迫拜訪順序遞增
    for i in stops:
        for j in stops:
            if i != j and i != DEPOT and j != DEPOT:
                tsp += u[i] - u[j] + n * x[(i, j)] <= n - 1

    tsp.solve(pulp.PULP_CBC_CMD(msg=0))
    assert pulp.LpStatus[tsp.status] == "Optimal", pulp.LpStatus[tsp.status]

    route = [DEPOT]
    while True:
        nxt = next(j for j in stops
                   if j != route[-1] and x[(route[-1], j)].value() > 0.5)
        route.append(nxt)
        if nxt == DEPOT:
            return route, pulp.value(tsp.objective)


print("\n=== 第二階段：每台車排最短路線 ===")
total = 0.0
total_radial = 0.0
for v in vehicles:
    route, length = solve_tsp([DEPOT] + groups[v])
    radial = sum(2 * dist(DEPOT, c) for c in groups[v])  # 每客戶單獨往返
    total += length
    total_radial += radial
    print(f"  {v}: {' → '.join(route)}")
    print(f"      路線距離 {length:.2f}（輻射式往返要 {radial:.2f}）")

print(f"\n  總行駛距離: {total:.2f}")
print(f"  比輻射式往返節省: {total_radial - total:.2f}"
      f"（{(total_radial - total) / total_radial * 100:.0f}%）")
