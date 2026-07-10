"""09. 下料問題：切割模式列舉 + 最少鋼管數（IP，以模式為決策變數）"""
import pulp

# ---------- 資料（示範用虛構數字） ----------
STOCK_LENGTH = 10               # 標準鋼管長度（米）
demand = {3: 25, 4: 20, 5: 15, 6: 10}  # {長度: 需求根數}


# ---------- 前處理：列舉所有切割模式 ----------
# 一種「模式」= 一根標準鋼管的一種切法，例如 {3: 2, 4: 1} = 切出 2 根 3 米 + 1 根 4 米
def enumerate_patterns(stock_length, lengths):
    patterns = []
    lengths = sorted(lengths, reverse=True)

    def extend(remaining, pattern, idx):
        if idx == len(lengths):
            if pattern:  # 排除什麼都不切的空模式
                patterns.append(dict(pattern))
            return
        length = lengths[idx]
        for count in range(remaining // length + 1):
            if count > 0:
                pattern[length] = count
            extend(remaining - length * count, pattern, idx + 1)
        pattern.pop(length, None)

    extend(stock_length, {}, 0)
    return patterns


patterns = enumerate_patterns(STOCK_LENGTH, demand.keys())
print(f"=== 共列舉出 {len(patterns)} 種切割模式 ===")

# ---------- 建模 ----------
prob = pulp.LpProblem("cutting_stock", pulp.LpMinimize)

# 決策變數：n[p] = 模式 p 使用幾次
n = pulp.LpVariable.dicts("pattern", range(len(patterns)),
                          lowBound=0, cat=pulp.LpInteger)

# 目標式：鋼管總數最小化
prob += pulp.lpSum(n.values()), "鋼管總數"

# 限制式：每種長度的產出 ≥ 需求（== 可能無解，超產算浪費）
for length, req in demand.items():
    prob += (pulp.lpSum(patterns[p].get(length, 0) * n[p]
                        for p in range(len(patterns)))
             >= req), f"需求_{length}m"

# ---------- 求解 ----------
prob.solve(pulp.PULP_CBC_CMD(msg=0))
assert pulp.LpStatus[prob.status] == "Optimal", pulp.LpStatus[prob.status]


# ---------- 結果 ----------
def pattern_str(p):
    return " + ".join(f"{cnt}×{length}m"
                      for length, cnt in sorted(p.items(), reverse=True))


total_pipes = 0
total_waste = 0.0
print("\n=== 切割方案 ===")
for p in range(len(patterns)):
    count = n[p].value()
    if count > 0.5:
        used_len = sum(length * cnt for length, cnt in patterns[p].items())
        waste = STOCK_LENGTH - used_len
        total_pipes += int(count)
        total_waste += waste * count
        print(f"  {pattern_str(patterns[p]):<20} × {int(count):>2} 根"
              f"（每根剩 {waste} 米）")

print("\n=== 需求檢查 ===")
over_len = 0  # 超產的總長度（米），也是浪費的一種
for length in sorted(demand):
    produced = sum(patterns[p].get(length, 0) * n[p].value()
                   for p in range(len(patterns)))
    extra = int(produced) - demand[length]
    over_len += extra * length
    print(f"  {length} 米：需求 {demand[length]:>2}，產出 {int(produced):>2}"
          + (f"（超產 {extra}）" if extra else ""))

used_total = total_pipes * STOCK_LENGTH
print(f"\n  使用鋼管:   {total_pipes} 根（{used_total} 米）")
print(f"  切邊浪費:   {total_waste:.0f} 米")
print(f"  超產浪費:   {over_len} 米")
print(f"  材料利用率: {(used_total - total_waste - over_len) / used_total * 100:.1f}%"
      "（需求內的有效產出 / 投入材料）")
