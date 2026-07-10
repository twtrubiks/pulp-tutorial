"""08. 數獨：三維 0/1 變數的純可行解問題（無目標式）"""
import pulp

# ---------- 題目（0 代表空格） ----------
puzzle = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

VALS = ROWS = COLS = range(9)

# ---------- 建模 ----------
prob = pulp.LpProblem("sudoku")  # 找可行解，不需要 LpMaximize/LpMinimize

# 決策變數：x[v][r][c] = 第 r 列第 c 行是否填數字 v+1
x = pulp.LpVariable.dicts("cell", (VALS, ROWS, COLS), cat=pulp.LpBinary)

# 無目標式（給常數 0，solver 只找可行解）
prob += 0, "無目標"

# 每格恰好填一個數字
for r in ROWS:
    for c in COLS:
        prob += pulp.lpSum(x[v][r][c] for v in VALS) == 1

# 每列、每行：每個數字恰好出現一次
for v in VALS:
    for r in ROWS:
        prob += pulp.lpSum(x[v][r][c] for c in COLS) == 1
    for c in COLS:
        prob += pulp.lpSum(x[v][r][c] for r in ROWS) == 1

# 每個 3x3 宮：每個數字恰好出現一次
for v in VALS:
    for br in range(3):
        for bc in range(3):
            prob += pulp.lpSum(x[v][r][c]
                               for r in range(br * 3, br * 3 + 3)
                               for c in range(bc * 3, bc * 3 + 3)) == 1

# 題目給的提示數字固定為 1
for r in ROWS:
    for c in COLS:
        if puzzle[r][c] != 0:
            prob += x[puzzle[r][c] - 1][r][c] == 1

# ---------- 求解 ----------
prob.solve(pulp.PULP_CBC_CMD(msg=0))
assert pulp.LpStatus[prob.status] == "Optimal", pulp.LpStatus[prob.status]

# ---------- 結果 ----------
print("=== 數獨解 ===")
for r in ROWS:
    if r % 3 == 0 and r > 0:
        print("  ------+-------+------")
    cells = []
    for c in COLS:
        v = next(v for v in VALS if x[v][r][c].value() > 0.5)
        cells.append(str(v + 1))
        if c in (2, 5):
            cells.append("|")
    print("  " + " ".join(cells))
