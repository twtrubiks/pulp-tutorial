# PuLP 實戰練習集

由淺入深的 11 個真實情境練習，每題一個資料夾，包含：

- `README.md`：題目描述、數學模型（決策變數 / 目標式 / 限制式）、延伸練習
- `solve.py`：可直接執行的完整解答

## 環境設定

```bash
pip install -r requirements.txt
```

> 注意：PuLP 官方文件（https://coin-or.github.io/pulp/）提到新版 CBC 不再保證內建
> （"CBC is not bundled with PuLP"），若 `pulp.listSolvers(onlyAvailable=True)`
> 看不到 `PULP_CBC_CMD`，請改用 `pip install "pulp[cbc]"`。
> 實測 `pulp 3.3.2` 安裝後 `PULP_CBC_CMD` 可用。

執行任一題（在專案根目錄）：

```bash
python practice/01_product_mix/solve.py
```

## 學習路線

| # | 題目 | 難度 | 變數型態 | 練習重點 |
|---|------|------|----------|----------|
| 01 | [生產組合](01_product_mix/) | 入門 | 連續 | LP 三件套：變數、目標式、限制式；shadow price |
| 02 | [飲食問題](02_diet_problem/) | 入門 | 整數 | 用真實感資料建模、模型迭代（加限制修正怪解） |
| 03 | [員工排班](03_staff_scheduling/) | 中級 | 整數 | 覆蓋式限制、循環排班建模 |
| 04 | [運輸問題](04_transportation/) | 中級 | 連續 | 二維決策變數、供需平衡 |
| 05 | [選股組合](05_stock_portfolio/) | 中級 | 0/1 + 整數 | 選擇變數與數量變數的連動（linking constraints） |
| 06 | [指派問題](06_assignment/) | 中級 | 0/1 | 一對一指派、不可行組合處理 |
| 07 | [設施選址](07_facility_location/) | 進階 | 0/1 + 連續 | 固定成本、big-M / 容量連動 |
| 08 | [數獨](08_sudoku/) | 進階 | 0/1 | 純可行解問題（無目標式）、三維 0/1 變數 |
| 09 | [下料問題](09_cutting_stock/) | 進階 | 整數 | 切割模式列舉、「以模式為變數」的建模視角 |
| 10 | [供應鏈網路](10_supply_chain/) | 進階 | 0/1 + 連續 | 多層級網路流、流量守恆（04 + 07 的綜合） |
| 11 | [車輛路徑](11_vehicle_routing/) | 進階 | 0/1 + 整數 | 分解策略、子迴圈消除（MTZ）、常數目標式陷阱 |

## 建議練習流程

每一題都照這個流程走，最後一步才是真正建立直覺的地方：

1. **定義決策變數**：先問「我能決定什麼？」
2. **寫目標式**：最大化或最小化什麼？
3. **寫限制式**：什麼條件不能違反？
4. **求解**：確認 `LpStatus` 是 `Optimal`
5. **檢查解合不合理**：怪解通常代表模型漏了限制，不是 solver 錯
6. **敏感度分析**：改資料（預算、需求、成本）重跑，觀察解怎麼變

## 進階閱讀

做完練習後，看 [實務應用指南](practical_guide.md)：
PuLP 在真實專案裡怎麼跟 pandas、批次排程、Web 服務、試算表、儀表板搭配，
以及什麼時候該換工具（cvxpy / CP-SAT / Pyomo）。

## 參考資源

- PuLP 官方文件：https://coin-or.github.io/pulp/
  （"PuLP is an linear and mixed integer programming modeler written in Python"——
  只能處理**線性**目標式與限制式，二次式如 Markowitz 變異數不在範圍內）
- 官方 Case Studies：https://coin-or.github.io/pulp/CaseStudies/index.html
  （Blending、Set Partitioning、Sudoku、Transportation、Two-Stage Production Planning）

## 資料聲明

各題使用的價格、營養成分、報酬率等數字皆為**示範用虛構資料**，
僅為了讓題目有真實感，並非任何商品或股票的真實數據。
