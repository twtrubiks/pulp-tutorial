# PuLP 實務應用指南

練習題會建模之後，真正的問題是：實務上這個套件怎麼跟其他東西組在一起用？
本文整理常見的搭配方式與部署型態。

> 聲明：除了標注官方文件來源的部分，本文屬於業界常見做法的經驗歸納，
> 沒有單一官方文件可引用。

## PuLP 的定位：管線中薄薄的一層

PuLP 的本職是「把 Python 寫的模型翻譯成 LP/MPS 格式、丟給 solver、把解讀回來」。
官方描述："PuLP can generate MPS or LP files and call solvers such as GLPK,
COIN-OR CLP/CBC, CPLEX, GUROBI, MOSEK, XPRESS, CHOCO, MIPCL, HiGHS,
SCIP/FSCIP, and OR-Tools CP-SAT."（https://coin-or.github.io/pulp/）

所以它從來不是主角，而是嵌在這樣的管線中間：

```
資料來源（DB / CSV / API）
   → pandas 整理係數
      → PuLP 建模 + solver 求解
         → 解轉回 DataFrame
            → 輸出（報表 / 寫回 DB / API 回應 / 儀表板）
```

## 六種常見搭配

### 1. pandas —— 幾乎必然的隊友

真實專案裡 90% 的工夫花在把髒資料整理成乾淨的係數，建模本身反而是小事。

實務寫法：把模型包成純函式，資料進、模型出，才能單元測試。

```python
def build_model(df: pd.DataFrame) -> pulp.LpProblem:
    """從整理好的 DataFrame 建模，不碰 IO、不碰全域狀態"""
    ...

# 測試：餵一個已知答案的小案例
def test_small_case():
    prob = build_model(tiny_df)
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    assert pulp.LpStatus[prob.status] == "Optimal"
    assert abs(pulp.value(prob.objective) - 42.0) < 1e-6
```

### 2. 排程批次 —— 最常見的部署型態

最佳化在實務上多半是**批次跑，不是即時算**：

- 每晚 cron（或 Airflow / Prefect）跑明天的生產計畫
- 每週產生下期班表
- 每日算補貨量 / 配送計畫

跑完把結果寫回 DB 或產報表給人看。

### 3. Web 服務 —— 包成內部 API

用 FastAPI / Django 把 optimizer 包成服務：前端送需求參數，後端解完回傳計畫。

實務關鍵：**MILP 求解時間不可預測**（可能一秒也可能十分鐘），所以——

- 絕不能在 request 執行緒裡解，要丟 Celery / RQ 背景任務
- 設 `timeLimit`（秒數上限）+ `gapRel`（相對 gap 容忍度）讓最壞情況有上限、
  接受「夠好」的解。兩個參數的官方定義（
  https://coin-or.github.io/pulp/technical/solvers.html ）：
  - `timeLimit (float)` – "maximum time for solver (in seconds)"
  - `gapRel (float)` – "relative gap tolerance for the solver to stop (in fraction)"
  - 另有 `warmStart (bool)` – "if True, the solver will use the current value
    of variables as a start"，重解相近問題時可加速

```python
prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=60, gapRel=0.01))
# 60 秒內回來，目標值離理論最佳差距 1% 以內就收工
```

### 4. Excel / Google Sheets 當使用者介面

內部工具最務實的形態：計畫人員在試算表裡改參數（需求、產能、成本），
批次任務讀進來、解完、把計畫寫回另一個分頁。使用者完全不用碰 Python。

### 5. Streamlit 儀表板做 what-if 分析

決策支援場景很吃「拉一下滑桿（預算 +10%？）→ 重解 → 看解怎麼變」的互動，
小模型秒解、體驗很好。

這裡有個實務本質：**最佳化輸出多半是給人審的建議，不是自動執行的指令**。
所以輸出要能解釋——印出哪些限制式是綁死的（binding）、影子價格多少，
計畫的人才會信任它（作法見練習 01 的影子價格輸出）。

### 6. Solver 抽換 —— PuLP 的核心賣點

開發用免費的 CBC，模型變大變慢後換 HiGHS 或商用的 Gurobi / CPLEX，
程式碼只改 `prob.solve(...)` 那一行的 solver 物件，模型完全不動。

很多團隊靠這點先用 PuLP 免費驗證價值，再決定要不要花錢買商用 solver。

## 實戰必備的三個技能（練習題沒覆蓋的）

練習題都是「資料寫死、一定有解、一秒解完」的乾淨題目，實戰還需要：

1. **Infeasible 除錯**：真實模型第一次跑常常是 `Infeasible`，solver 不會告訴你
   是哪條限制式打架。實務手法是「彈性限制」——每條硬限制配一個帶重罰的
   鬆弛變數，看最佳解裡哪個鬆弛變數非零，就知道是誰在作怪。
   好處是服務永遠回得出一個計畫＋一份違規報告，而不是兩手一攤。

2. **多目標**：真實問題很少只有一個目標（排班要人數少「且」班表公平）。
   標準做法：加權合成單一目標，或字典序法
   （先解目標一 → 固定成限制式 → 再解目標二）。

3. **Solver 控制**：見上面第 3 節的 `timeLimit` / `gapRel` / `warmStart`。

## 什麼時候該從 PuLP 畢業

工具選錯，建模再漂亮都是白工：

| 問題型態 | 建議工具 | 原因 |
|---------|---------|------|
| 中小型線性問題（LP/MILP） | **PuLP** | 甜蜜點：從資料到決策最省事 |
| 凸二次目標（變異數、夏普比率） | cvxpy | PuLP 只能線性（官方定位即 "linear and mixed integer programming modeler"） |
| 重組合排程（大型排班、工單排程） | OR-Tools CP-SAT | constraint programming 通常比 MILP 好解；PuLP 也能直接把模型丟給 CP-SAT（見官方 solver 清單） |
| 非線性 / 更完整建模生態 | Pyomo | Pyomo 官網的自我定位（此點未逐一驗證，採用前請自行確認） |
