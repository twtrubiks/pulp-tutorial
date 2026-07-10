# pulp-tutorial

PuLP 中文教學與實戰練習集——用 Python 解線性規劃（LP）與混合整數規劃（MILP）問題。

從 5 分鐘快速上手開始，到 11 題由淺入深的實戰練習（生產組合、排班、運輸、
選址、下料、供應鏈、車輛路徑⋯⋯），每題都附**數學模型推導**與**可直接執行的解答**。

## 什麼是 PuLP？

[PuLP](https://github.com/coin-or/pulp) 是 COIN-OR 專案的開源 Python 建模工具，
讓你用貼近數學式的語法描述優化問題，內建免費的 CBC solver 求解。
30 秒看一個例子——利潤最大化：

```python
import pulp

prob = pulp.LpProblem("利潤最大化", pulp.LpMaximize)

x = pulp.LpVariable("產品A", lowBound=0)
y = pulp.LpVariable("產品B", lowBound=0)

prob += 30 * x + 20 * y, "總利潤"          # 目標式
prob += 1 * x + 2 * y <= 100, "機器時間"   # 限制式
prob += 3 * x + 1 * y <= 120, "人工時間"

prob.solve(pulp.PULP_CBC_CMD(msg=0))
print(pulp.LpStatus[prob.status], x.varValue, y.varValue)
```

## 安裝

```bash
pip install -r requirements.txt
```

> 若 `pulp.listSolvers(onlyAvailable=True)` 看不到 `PULP_CBC_CMD`，
> 改用 `pip install "pulp[cbc]"`，詳見 [practice/README.md](practice/README.md)。

## 內容導覽

| 內容 | 說明 |
|------|------|
| [quick_start.md](quick_start.md) | 5 分鐘快速上手：核心流程、常用模板、常見錯誤 |
| [tutorial.md](tutorial.md) | 完整教學：變數類型、邏輯約束線性化、固定成本處理、除錯技巧、優缺點分析 |
| [practice/](practice/) | **11 題實戰練習**（本 repo 的主體） |
| [practice/practical_guide.md](practice/practical_guide.md) | 實務應用指南：與 pandas / 排程 / Web 服務的搭配，以及何時該換工具 |

## 實戰練習一覽

| # | 題目 | 難度 | 練習重點 |
|---|------|------|----------|
| 01 | [生產組合](practice/01_product_mix/) | 入門 | LP 三件套、shadow price |
| 02 | [飲食問題](practice/02_diet_problem/) | 入門 | 整數規劃、模型迭代 |
| 03 | [員工排班](practice/03_staff_scheduling/) | 中級 | 覆蓋式限制、循環班型 |
| 04 | [運輸問題](practice/04_transportation/) | 中級 | 二維變數、供需平衡 |
| 05 | [選股組合](practice/05_stock_portfolio/) | 中級 | 0/1 選擇變數、連動限制 |
| 06 | [指派問題](practice/06_assignment/) | 中級 | 一對一指派、不可行組合 |
| 07 | [設施選址](practice/07_facility_location/) | 進階 | 固定成本、big-M 連動 |
| 08 | [數獨](practice/08_sudoku/) | 進階 | 純可行解問題、三維 0/1 變數 |
| 09 | [下料問題](practice/09_cutting_stock/) | 進階 | 切割模式列舉、以模式為變數 |
| 10 | [供應鏈網路](practice/10_supply_chain/) | 進階 | 多層級網路流、流量守恆 |
| 11 | [車輛路徑](practice/11_vehicle_routing/) | 進階 | 分解策略、MTZ 子迴圈消除 |

## 建議學習路徑

1. 讀 [quick_start.md](quick_start.md)，跑通第一個範例
2. 照順序做 [practice/](practice/) 的 01 → 11，每題先自己建模再看解答
3. 觀念不熟時回 [tutorial.md](tutorial.md) 查對應章節
4. 做完看 [實務應用指南](practice/practical_guide.md)，了解 PuLP 在真實專案的位置

## 參考資料

**官方**：

- PuLP 官方文件：https://coin-or.github.io/pulp/
- 官方 Case Studies：https://coin-or.github.io/pulp/CaseStudies/index.html

## 資料聲明

練習題中的價格、營養成分、報酬率等數字皆為示範用虛構資料。

## License

[MIT](LICENSE)
