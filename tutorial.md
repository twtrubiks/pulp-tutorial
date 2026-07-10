# PuLP Python 套件完整教學指南

## 目錄
1. [PuLP 簡介](#pulp-簡介)
2. [核心概念](#核心概念)
3. [安裝與設定](#安裝與設定)
4. [基本使用流程](#基本使用流程)
5. [變數類型詳解](#變數類型詳解)
6. [實戰範例](#實戰範例)
7. [進階應用](#進階應用)
8. [優缺點分析](#優缺點分析)
9. [最佳實踐建議](#最佳實踐建議)

---

## PuLP 簡介

### 什麼是 PuLP？

PuLP 是一個用 Python 編寫的開源線性規劃（Linear Programming, LP）建模工具，專門用於解決最佳化問題。它的主要特色是：

- **易於使用**：使用直覺的 Python 語法定義優化問題
- **功能強大**：支援線性規劃（LP）、整數規劃（ILP）和混合整數規劃（MILP）
- **求解器整合**：內建 CBC 求解器，也可整合其他商業或開源求解器
- **應用廣泛**：適用於資源分配、生產排程、物流規劃等多種領域

### 歷史背景

線性規劃在運籌學中有重要地位，Leonid Kantorovich 因使用線性規劃解決最優資源分配問題，獲得了 1975 年諾貝爾經濟學獎。PuLP 將這個強大的數學工具以簡單易用的方式帶給 Python 開發者。

---

## 核心概念

### 什麼是線性規劃？

**線性規劃**是在線性等式或不等式約束下，最大化或最小化線性目標函數的數學方法。

#### 線性規劃的基本要素：

1. **決策變數（Decision Variables）**
   - 需要求解的未知數
   - 例如：各產品的生產數量、各銀行的存款金額

2. **目標函數（Objective Function）**
   - 要最大化或最小化的目標
   - 例如：最大化利潤、最小化成本

3. **限制條件（Constraints）**
   - 決策變數必須滿足的條件
   - 例如：資源限制、時間限制、預算限制

### 數學表達式範例

**最大化問題：**
```
最大化：Z = 3x + 2y
限制條件：
  x + y ≤ 10
  2x + y ≤ 15
  x ≥ 0, y ≥ 0
```

---

## 安裝與設定

### 安裝 PuLP

```bash
# 使用 pip 安裝
pip install pulp
```

### 驗證安裝

```python
import pulp

# 檢查版本
print(pulp.__version__)

# 檢查可用的求解器
print(pulp.listSolvers(onlyAvailable=True))
```

---

## 基本使用流程

PuLP 的使用遵循五個標準步驟，一次看完
（逐步拆解的新手教學見 [quick_start.md](quick_start.md)，這裡不重複）：

```python
import pulp

# 1. 建立問題物件（最大化用 LpMaximize，最小化用 LpMinimize）
prob = pulp.LpProblem("問題名稱", pulp.LpMaximize)

# 2. 定義決策變數
x = pulp.LpVariable("x", lowBound=0)
y = pulp.LpVariable("y", lowBound=0)

# 3. 設定目標函數（用 += 添加）
prob += 3*x + 2*y, "目標函數描述"

# 4. 添加限制條件
prob += x + y <= 10, "限制條件1"
prob += 2*x + y <= 15, "限制條件2"

# 5. 求解並查看結果
prob.solve()
print("狀態:", pulp.LpStatus[prob.status])
print("x =", x.varValue, "y =", y.varValue)
print("最優解 =", pulp.value(prob.objective))
```

---

## 變數類型詳解

### 1. 連續變數（Continuous）

```python
# 可以取任意實數值
x = pulp.LpVariable("x", lowBound=0, upBound=100, cat="Continuous")
```

**應用場景：**
- 產品配方比例
- 投資金額分配
- 原料用量

### 2. 整數變數（Integer）

```python
# 只能取整數值
y = pulp.LpVariable("y", lowBound=0, cat="Integer")
```

**應用場景：**
- 產品生產數量
- 員工排班人數
- 運輸車輛數

### 3. 二元變數（Binary）

```python
# 只能取 0 或 1
z = pulp.LpVariable("z", cat="Binary")
```

**應用場景：**
- 決定是否生產某產品（0 = 不生產，1 = 生產）
- 設施是否啟用
- 路徑選擇

---

## 實戰範例

### 範例 1：基礎利潤最大化問題

**問題描述：**
一家工廠生產產品 A 和產品 B：
- 產品 A 每單位利潤 30 元，需要 1 小時機器時間和 3 小時人工
- 產品 B 每單位利潤 20 元，需要 2 小時機器時間和 1 小時人工
- 每日機器時間上限 100 小時，人工時間上限 120 小時

**求解：如何安排生產以最大化利潤？**

```python
import pulp

# 步驟 1: 建立問題
prob = pulp.LpProblem("利潤最大化", pulp.LpMaximize)

# 步驟 2: 定義決策變數
A = pulp.LpVariable("產品A", lowBound=0, cat="Integer")
B = pulp.LpVariable("產品B", lowBound=0, cat="Integer")

# 步驟 3: 目標函數（最大化利潤）
prob += 30*A + 20*B, "總利潤"

# 步驟 4: 限制條件
prob += 1*A + 2*B <= 100, "機器時間限制"
prob += 3*A + 1*B <= 120, "人工時間限制"

# 步驟 5: 求解
prob.solve()

# 輸出結果
print("求解狀態:", pulp.LpStatus[prob.status])
print(f"最優解：生產產品A {A.varValue} 單位，產品B {B.varValue} 單位")
print(f"最大利潤: {pulp.value(prob.objective)} 元")
```

**輸出結果：**
```
求解狀態: Optimal
最優解：生產產品A 28.0 單位，產品B 36.0 單位
最大利潤: 1560.0 元
```

---

### 範例 2：銀行存款利率優化

**問題描述：**
你有 100 萬元要存入不同銀行：
- 銀行 A：年利率 3.5%，最低存款 20 萬
- 銀行 B：年利率 3.0%，無限制
- 銀行 C：年利率 4.0%，最高存款 30 萬

**目標：最大化年利息收入**

```python
import pulp

# 建立問題
prob = pulp.LpProblem("銀行存款優化", pulp.LpMaximize)

# 定義變數（單位：萬元）
bank_A = pulp.LpVariable("銀行A", lowBound=20, upBound=100)
bank_B = pulp.LpVariable("銀行B", lowBound=0, upBound=100)
bank_C = pulp.LpVariable("銀行C", lowBound=0, upBound=30)

# 目標函數（最大化利息，單位：萬元）
prob += 0.035*bank_A + 0.030*bank_B + 0.040*bank_C, "總利息"

# 限制條件：總存款為 100 萬
prob += bank_A + bank_B + bank_C == 100, "總金額限制"

# 求解
prob.solve()

# 輸出結果
print("求解狀態:", pulp.LpStatus[prob.status])
print(f"銀行A存款: {bank_A.varValue:.2f} 萬元")
print(f"銀行B存款: {bank_B.varValue:.2f} 萬元")
print(f"銀行C存款: {bank_C.varValue:.2f} 萬元")
print(f"年利息收入: {pulp.value(prob.objective):.4f} 萬元 = {pulp.value(prob.objective)*10000:.2f} 元")
```

---

### 範例 3：寵物食品配方優化

**問題描述：**
製作寵物食品需要滿足營養需求並最小化成本：

```python
import pulp

# 建立問題
prob = pulp.LpProblem("寵物食品配方", pulp.LpMinimize)

# 原料資訊（成本、蛋白質含量、脂肪含量）單位：元/kg, g/kg
ingredients = {
    "雞肉": {"cost": 50, "protein": 200, "fat": 50},
    "米飯": {"cost": 10, "protein": 20, "fat": 5},
    "蔬菜": {"cost": 15, "protein": 30, "fat": 2},
}

# 決策變數：各原料用量（kg）
amounts = pulp.LpVariable.dicts("amount", ingredients.keys(), lowBound=0)

# 目標函數：最小化成本
prob += pulp.lpSum([amounts[i] * ingredients[i]["cost"] for i in ingredients]), "總成本"

# 限制條件：營養需求
prob += pulp.lpSum([amounts[i] * ingredients[i]["protein"] for i in ingredients]) >= 500, "蛋白質需求"
prob += pulp.lpSum([amounts[i] * ingredients[i]["fat"] for i in ingredients]) >= 100, "脂肪需求"

# 限制條件：總重量為 5 kg
prob += pulp.lpSum([amounts[i] for i in ingredients]) == 5, "總重量"

# 求解
prob.solve()

# 輸出結果
print("狀態:", pulp.LpStatus[prob.status])
for ingredient in ingredients:
    print(f"{ingredient}: {amounts[ingredient].varValue:.3f} kg")
print(f"最低成本: {pulp.value(prob.objective):.2f} 元")
```

---

## 進階應用

### 1. 邏輯約束的線性化

在線性規劃中，需要將邏輯運算轉換為線性約束。

#### AND 邏輯（與）

如果 `y1 = 1` 且 `y2 = 1`，則 `z = 1`：

```python
z = pulp.LpVariable("z", cat="Binary")
y1 = pulp.LpVariable("y1", cat="Binary")
y2 = pulp.LpVariable("y2", cat="Binary")

# z = y1 AND y2 的線性化
prob += z <= y1
prob += z <= y2
prob += z >= y1 + y2 - 1
```

#### OR 邏輯（或）

如果 `y1 = 1` 或 `y2 = 1`，則 `z = 1`：

```python
# z = y1 OR y2 的線性化
prob += z >= y1
prob += z >= y2
prob += z <= y1 + y2
```

#### NOT 邏輯（非）

```python
# z = NOT y 的線性化
prob += z == 1 - y
```

### 2. 固定成本處理

許多實際問題包含固定成本（例如啟動成本）：

```python
# 如果生產產品 x，需支付固定成本 F
x = pulp.LpVariable("x", lowBound=0)
y = pulp.LpVariable("y", cat="Binary")  # 是否生產的指標

cost_per_unit = 5   # 每單位變動成本
fixed_cost = 1000   # 固定成本（有生產才發生）
M = 10000  # 一個足夠大的數（Big-M）

# 如果 x > 0，則 y = 1
prob += x <= M * y

# 目標函數包含固定成本和可變成本
prob += cost_per_unit * x + fixed_cost * y, "總成本"
```

### 3. 整合外部求解器

PuLP 可以使用多種求解器：

```python
# 使用 CPLEX
prob.solve(pulp.CPLEX())

# 使用 GUROBI
prob.solve(pulp.GUROBI())

# 使用 GLPK
prob.solve(pulp.GLPK())

# 檢查可用的求解器
print(pulp.listSolvers(onlyAvailable=True))
```

### 4. 求解器參數調整

```python
# 設定時間限制和其他參數
solver = pulp.PULP_CBC_CMD(
    timeLimit=60,  # 最多求解 60 秒
    gapRel=0.01,   # 允許 1% 的最優性間隙
    msg=1          # 顯示求解過程訊息
)

prob.solve(solver)
```

---

## 優缺點分析

### ✅ 優點

#### 1. **易於學習和使用**
- **直覺的 Python 語法**：不需要深厚的數學背景即可使用
- **文檔完整**：有豐富的範例和教學資源
- **快速原型開發**：幾行程式碼即可建立優化模型

```python
# 簡潔的語法範例
prob = pulp.LpProblem("問題", pulp.LpMaximize)
x = pulp.LpVariable("x", lowBound=0)
prob += 3*x, "目標"
prob += x <= 10, "限制"
prob.solve()
```

#### 2. **功能強大**
- **支援多種問題類型**：LP、ILP、MILP
- **多種變數類型**：連續、整數、二元變數
- **靈活的建模能力**：可處理複雜的實際問題

#### 3. **求解器整合**
- **內建 CBC 求解器**：無需額外安裝即可使用
- **支援多種求解器**：CPLEX、Gurobi、GLPK 等
- **易於切換**：一行程式碼即可更換求解器

#### 4. **開源免費**
- **MIT 授權**：商業和個人使用都免費
- **活躍的社群**：有持續的維護和更新
- **豐富的生態系統**：與 NumPy、Pandas 等整合良好

#### 5. **廣泛的應用領域**
- 供應鏈管理與物流優化
- 生產排程與資源分配
- 金融投資組合優化
- 能源系統規劃
- 人力資源排班

### ❌ 缺點

#### 1. **效能限制**
- **大規模問題**：對於超大規模問題（數十萬變數），效能不如專業求解器
- **非線性問題**：不支援非線性優化（需要其他工具如 Pyomo、SciPy）
- **內建求解器較慢**：CBC 求解器在某些情況下比商業求解器慢

**解決方案：**
```python
# 對於大規模問題，切換到商業求解器
prob.solve(pulp.GUROBI())  # 需要授權
```

#### 2. **建模抽象層級**
- **較低階的 API**：相比 Pyomo 等工具，缺少一些高階建模功能
- **沒有自動微分**：無法自動計算梯度（非線性問題需要）
- **有限的代數結構**：複雜模型需要手動展開

#### 3. **除錯困難**
- **不可行解診斷**：當問題無解時，難以找出衝突的約束條件
- **錯誤訊息不明確**：有時需要手動檢查模型
- **沒有內建視覺化**：需要額外工具來視覺化模型結構

**改善方法：**
```python
# 檢查求解狀態
if prob.status != pulp.LpStatusOptimal:
    print("無最優解！狀態:", pulp.LpStatus[prob.status])

    # 輸出模型到文件進行檢查
    prob.writeLP("model.lp")
```

#### 4. **文檔和範例**
- **進階主題較少**：複雜應用的範例不多
- **API 文檔簡略**：某些功能缺少詳細說明
- **中文資源有限**：大部分教學資源為英文

#### 5. **特定限制**
- **不支援二次規劃**：二次目標函數或約束需要其他工具
- **隨機優化**：不直接支援隨機規劃
- **多目標優化**：需要手動實現權重法或約束法

### 📊 與其他工具比較

| 特性 | PuLP | Pyomo | Gurobi | SciPy.optimize |
|------|------|-------|--------|----------------|
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 功能完整性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 效能 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 開源免費 | ✅ | ✅ | ❌（需授權） | ✅ |
| 線性規劃 | ✅ | ✅ | ✅ | ✅ |
| 非線性規劃 | ❌ | ✅ | ✅ | ✅ |
| 學習曲線 | 平緩 | 陡峭 | 中等 | 中等 |

---

## 最佳實踐建議

### 1. 模型建構建議

#### ✅ 好的做法

```python
# 使用字典管理變數
products = ["A", "B", "C"]
x = pulp.LpVariable.dicts("product", products, lowBound=0, cat="Integer")

# 使用 lpSum 而非 sum
prob += pulp.lpSum([profit[p] * x[p] for p in products]), "總利潤"

# 為約束條件命名
prob += x["A"] + x["B"] <= 100, "產能限制_AB"
```

#### ❌ 避免的做法

```python
# 不要使用 Python sum（能動也不會警告，但逐項相加會反覆建立中間運算式，變數多時很慢）
prob += sum([profit[p] * x[p] for p in products])

# 不要忘記設定變數下界（避免負值）
x = pulp.LpVariable("x")  # 預設可以為負數！

# 不要使用無意義的約束名稱
prob += x <= 10, "constraint1"
```

### 2. 除錯技巧

```python
# 1. 輸出模型到檔案檢查
prob.writeLP("model.lp")

# 2. 檢查求解狀態
status_messages = {
    pulp.LpStatusOptimal: "找到最優解",
    pulp.LpStatusNotSolved: "尚未求解",
    pulp.LpStatusInfeasible: "無可行解（約束條件衝突）",
    pulp.LpStatusUnbounded: "無界（缺少約束）",
}
print(status_messages.get(prob.status, "未知狀態"))

# 3. 驗證變數值
for v in prob.variables():
    if v.varValue is not None:
        print(f"{v.name} = {v.varValue}")

# 4. 檢查約束鬆弛度（slack）
for name, constraint in prob.constraints.items():
    print(f"{name}: slack = {constraint.slack}")
```

### 3. 效能優化

```python
# 1. 減少不必要的變數
# 如果 y = 2x，不需要定義 y 為變數，直接用 2*x

# 2. 使用適當的變數類型
# 如果變數必須是整數，明確指定 cat="Integer"

# 3. 緊湊的約束條件
# 避免冗餘約束，移除顯而易見的條件

# 4. 使用更快的求解器
# 對於大問題，考慮商業求解器
solver = pulp.GUROBI_CMD(options=[("TimeLimit", 300)])
prob.solve(solver)
```

### 4. 程式碼組織

```python
def create_production_model(products, demands, capacities):
    """
    建立生產規劃模型

    Args:
        products: 產品列表
        demands: 需求字典
        capacities: 產能字典

    Returns:
        prob: PuLP 問題物件
        x: 決策變數字典
    """
    # 建立問題
    prob = pulp.LpProblem("生產規劃", pulp.LpMinimize)

    # 定義變數
    x = pulp.LpVariable.dicts("production", products, lowBound=0, cat="Integer")

    # 添加約束
    for product in products:
        prob += x[product] >= demands[product], f"需求_{product}"

    return prob, x

# 使用函數
prob, x = create_production_model(
    products=["A", "B"],
    demands={"A": 100, "B": 50},
    capacities={"A": 200, "B": 100}
)
```

### 5. 常見錯誤與解決

| 錯誤 | 原因 | 解決方法 |
|------|------|----------|
| `Infeasible` | 約束條件互相矛盾 | 放寬部分約束或檢查數據 |
| `Unbounded` | 缺少上界約束 | 添加合理的上界 |
| `Not Solved` | 忘記求解 | 確保呼叫 `prob.solve()` |
| 變數值為 `None` | 求解失敗 | 檢查求解狀態 |
| 結果不合理 | 模型錯誤 | 檢查目標函數和約束 |

---

## 實用資源

### 官方文檔
- PuLP 官方文檔: https://coin-or.github.io/pulp/
- PuLP GitHub: https://github.com/coin-or/pulp

### 學習資源
- 線性規劃基礎理論
- 運籌學教科書
- Coursera 優化課程

### 相關工具
- **Pyomo**: 更強大但複雜的優化建模語言
- **CVXPY**: 凸優化專用
- **OR-Tools**: Google 的優化工具包

---

## 總結

PuLP 是一個優秀的 Python 線性規劃工具，特別適合：

✅ **適合使用的情境：**
- 初學者學習線性規劃
- 中小規模的優化問題
- 快速原型開發
- 不需要非線性優化的應用
- 預算有限（開源免費）

❌ **不適合的情境：**
- 超大規模問題（百萬級變數）
- 非線性優化問題
- 需要高度自訂求解器的場景
- 需要隨機或動態優化

### 學習建議

1. **從簡單開始**：先掌握基本的 LP 問題
2. **多做練習**：通過實際案例鞏固概念
3. **理解數學**：了解線性規劃的數學原理
4. **閱讀文檔**：熟悉 API 的各種用法
5. **參考範例**：學習他人的建模技巧

PuLP 的設計哲學是「簡單易用」，讓更多人能夠使用數學優化解決實際問題。希望這份教學能幫助你快速上手 PuLP，並在工作和學習中發揮它的價值！
