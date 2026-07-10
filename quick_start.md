# PuLP 快速入門指南

## 5 分鐘快速上手 PuLP

本指南將帶你在 5 分鐘內學會使用 PuLP 解決優化問題。

---

## 安裝

```bash
pip install pulp
```

---

## 第一個範例：簡單的利潤最大化

假設你有一家小工廠，生產兩種產品：

- **產品 A**：每個利潤 30 元，需要 1 小時機器時間
- **產品 B**：每個利潤 20 元，需要 2 小時機器時間
- **限制**：每天只有 100 小時機器時間

**問題**：應該生產多少產品 A 和 B 來最大化利潤？

### 完整程式碼

```python
import pulp

# 1. 建立問題（最大化利潤）
prob = pulp.LpProblem("利潤最大化", pulp.LpMaximize)

# 2. 定義變數（生產數量，必須 >= 0）
A = pulp.LpVariable("產品A", lowBound=0, cat="Integer")
B = pulp.LpVariable("產品B", lowBound=0, cat="Integer")

# 3. 設定目標函數（總利潤）
prob += 30*A + 20*B, "總利潤"

# 4. 添加限制條件（機器時間）
prob += 1*A + 2*B <= 100, "機器時間限制"

# 5. 求解
prob.solve()

# 6. 查看結果
print(f"產品A: {A.varValue} 個")
print(f"產品B: {B.varValue} 個")
print(f"最大利潤: {pulp.value(prob.objective)} 元")
```

### 輸出結果

```
產品A: 100.0 個
產品B: 0.0 個
最大利潤: 3000.0 元
```

> 為什麼全做產品 A？每小時機器時間的利潤：A 是 30 元，B 只有 10 元（20 元 ÷ 2 小時），
> 所以 100 小時全部拿來做 A 最划算。

---

## 核心概念解釋

### 1. 建立問題

```python
prob = pulp.LpProblem("問題名稱", pulp.LpMaximize)  # 最大化
# 或
prob = pulp.LpProblem("問題名稱", pulp.LpMinimize)  # 最小化
```

### 2. 定義變數

```python
# 連續變數（可以是小數）
x = pulp.LpVariable("x", lowBound=0)

# 整數變數
y = pulp.LpVariable("y", lowBound=0, cat="Integer")

# 二元變數（只能是 0 或 1）
z = pulp.LpVariable("z", cat="Binary")

# 有上下界的變數
w = pulp.LpVariable("w", lowBound=10, upBound=100)
```

### 3. 目標函數

```python
# 使用 += 添加目標函數
prob += 3*x + 2*y, "目標描述"
```

### 4. 限制條件

```python
# 添加不等式約束
prob += x + y <= 10, "限制1"
prob += 2*x + 3*y >= 5, "限制2"

# 添加等式約束
prob += x + y == 15, "限制3"
```

### 5. 求解並查看結果

```python
# 求解
prob.solve()

# 檢查狀態
print("狀態:", pulp.LpStatus[prob.status])
# 可能的狀態：Optimal（最優解）、Infeasible（無解）、Unbounded（無界）

# 查看變數值
print("x =", x.varValue)

# 查看目標函數值
print("最優解 =", pulp.value(prob.objective))
```

---

## 常見的求解狀態

| 狀態 | 意義 | 可能原因 |
|------|------|----------|
| `Optimal` | 找到最優解 | ✅ 正常 |
| `Infeasible` | 無可行解 | 約束條件互相衝突 |
| `Unbounded` | 目標函數無界 | 缺少必要的上下界約束 |
| `Not Solved` | 尚未求解 | 忘記呼叫 `.solve()` |

---

## 實用範例：預算分配

假設你有 10,000 元預算，想投資三種產品：

- **產品 X**：每單位成本 100 元，預期收益 15 元
- **產品 Y**：每單位成本 150 元，預期收益 25 元
- **產品 Z**：每單位成本 80 元，預期收益 12 元

**限制**：
- 至少要購買 10 單位產品 X
- 產品 Y 和 Z 合計不超過 50 單位

**目標**：最大化總收益

### 程式碼

```python
import pulp

# 建立問題
prob = pulp.LpProblem("預算分配", pulp.LpMaximize)

# 定義變數
X = pulp.LpVariable("產品X", lowBound=10, cat="Integer")  # 至少 10 單位
Y = pulp.LpVariable("產品Y", lowBound=0, cat="Integer")
Z = pulp.LpVariable("產品Z", lowBound=0, cat="Integer")

# 目標函數：最大化收益
prob += 15*X + 25*Y + 12*Z, "總收益"

# 限制條件
prob += 100*X + 150*Y + 80*Z <= 10000, "預算限制"
prob += Y + Z <= 50, "產品YZ數量限制"

# 求解
prob.solve()

# 輸出結果
print(f"狀態: {pulp.LpStatus[prob.status]}")
print(f"產品X: {X.varValue} 單位")
print(f"產品Y: {Y.varValue} 單位")
print(f"產品Z: {Z.varValue} 單位")
print(f"總成本: {100*X.varValue + 150*Y.varValue + 80*Z.varValue} 元")
print(f"最大收益: {pulp.value(prob.objective)} 元")
```

---

## 進階技巧：使用字典管理多個變數

當有很多相似的變數時，使用字典會更方便：

```python
import pulp

# 產品列表
products = ["A", "B", "C"]

# 一次創建多個變數
x = pulp.LpVariable.dicts("產量", products, lowBound=0, cat="Integer")

# 產品資訊
profit = {"A": 30, "B": 25, "C": 20}
time_needed = {"A": 2, "B": 3, "C": 1}

# 建立問題
prob = pulp.LpProblem("生產規劃", pulp.LpMaximize)

# 目標函數
prob += pulp.lpSum([profit[p] * x[p] for p in products]), "總利潤"

# 限制條件
prob += pulp.lpSum([time_needed[p] * x[p] for p in products]) <= 100, "時間限制"

# 求解
prob.solve()

# 輸出結果
for p in products:
    print(f"產品{p}: {x[p].varValue} 單位")
```

---

## 除錯技巧

除錯技巧（檢查求解狀態、輸出 `.lp` 模型檔、檢視變數值與約束鬆弛度）
統一整理在 [tutorial.md](tutorial.md) 的「最佳實踐建議 → 除錯技巧」，這裡不重複。

---

## 常見錯誤與解決方法

### 錯誤 1: 變數值為負數

```python
# ❌ 錯誤：忘記設定 lowBound
x = pulp.LpVariable("x")

# ✅ 正確：設定 lowBound=0
x = pulp.LpVariable("x", lowBound=0)
```

### 錯誤 2: 使用 Python sum 而非 lpSum

```python
# ❌ 不建議：內建 sum 能動，但逐項相加會反覆建立中間運算式，變數多時很慢
prob += sum([x[i] for i in range(10)])

# ✅ 正確：使用 pulp.lpSum
prob += pulp.lpSum([x[i] for i in range(10)])
```

### 錯誤 3: 忘記求解

```python
prob = pulp.LpProblem("問題", pulp.LpMaximize)
x = pulp.LpVariable("x", lowBound=0)
prob += 3*x

# ❌ 忘記呼叫 solve()
print(x.varValue)  # 會是 None！

# ✅ 記得求解
prob.solve()
print(x.varValue)  # 正確的值
```

---

## 下一步學習

1. **閱讀完整教學**：參考 [tutorial.md](tutorial.md)
2. **實戰練習**：做 [practice/](practice/) 的 11 題練習，由淺入深
3. **解決實際問題**：嘗試用 PuLP 解決你工作中的優化問題
4. **深入學習**：
   - 線性規劃理論
   - 整數規劃技巧
   - 求解器原理

---

## 常用程式碼片段

### 問題模板

```python
import pulp

# 最大化問題；最小化問題把 LpMaximize 改成 LpMinimize 即可
prob = pulp.LpProblem("問題名稱", pulp.LpMaximize)
x = pulp.LpVariable("x", lowBound=0)
y = pulp.LpVariable("y", lowBound=0)

prob += 目標函數表達式, "目標"
prob += 約束條件1, "約束1"
prob += 約束條件2, "約束2"

prob.solve()

print("狀態:", pulp.LpStatus[prob.status])
print("x =", x.varValue)
print("y =", y.varValue)
print("最優解 =", pulp.value(prob.objective))
```

---

## 小結

PuLP 的核心流程就是：

1. **建立問題** → `LpProblem()`
2. **定義變數** → `LpVariable()`
3. **設定目標** → `+=` 目標函數
4. **添加約束** → `+=` 限制條件
5. **求解** → `.solve()`
6. **查看結果** → `.varValue` 和 `value()`

只要掌握這六個步驟，就能開始使用 PuLP 解決大多數優化問題了！

祝學習愉快！ 🚀
