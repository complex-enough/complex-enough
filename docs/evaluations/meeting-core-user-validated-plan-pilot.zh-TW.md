# Meeting core 使用者驗證 Plan Pilot

- 評估日期：2026-08-31
- 評估範圍：Plan 品質與避免過度設計；不評技術 Spec 或 implementation
- 任務：物業管理入口的非緊急修繕到訪協調
- 狀態：Pilot 流程完成；`PILOT_PROTOCOL_PASS`、`DIRECTIONAL_POSITIVE`
- Design revision：`planrev-core-plan-maintenance-design-r1`
- Review revision：`planrev-core-plan-maintenance-review-r1`

## 白話結論

在這一個 Pilot 中，先讓 Main、領域專業與模擬終端使用者釐清實際任務，再由 Main 產生 Plan，明顯勝過一般單一 Agent 直接規劃。

三位完全 fresh 的模擬租戶盲評者都選擇 Treatment，且都判定差距為中等。Treatment 平均 `4.708/5`，一般 Agent Control 為 `4.104/5`，差距 `+0.604`。最大改善不是技術架構，而是：

- 清楚指出哪份時段、聯絡與進入資料目前有效；
- 區分租戶提議、辦公室確認、修改請求與修改已生效；
- 在改期、同時編輯或承包商可能已被聯絡時，提供可理解的結果與恢復路徑；
- 刪除完整逐筆歷史等非最低必要設計，沒有因多視角而變得更複雜。

這正面支持目前的產品假設：meeting skill 的主要價值可以放在技術 Spec 之前，以 `Main＋領域專業＋End user` 改善 Plan，使後續普通 Agent 更容易沿正常流程產生 Spec。它不支持「所有任務都一定提升」，也不能由單一模擬 Pilot 推論普遍 effect size。

## 要回答的問題

對一個小型、具有真實操作後果的 UIUX 任務，下列 Treatment 是否能比一般單一 Agent 產生更符合實際情境、較不容易誤操作、且不過度設計的 Plan？

```text
Main
  + 一位領域專業角色
  + 一位先做 unanchored opening、再檢查 UI claims 的模擬 End user
  → Main 綜合成 validated Plan
```

本次刻意不加入前端、後端、架構或資安席位。原因不是否認技術限制，而是把實驗邊界固定在「使用者要完成什麼、流程是否合理、資訊與恢復是否清楚」。技術端預期在 Plan 穩定後，沿一般 Agent 的 Plan → Spec 流程處理；本 Pilot 不驗證該後半段。

## 任務與共同限制

既有物業管理入口可讓租戶提出非緊急修繕，辦公室人工分流，承包商沿用既有工單。新增功能只需讓租戶：

- 提出最多三個到訪時段；
- 提供聯絡與物業進入說明；
- 回覆辦公室確認或改期要求；
- 在確認或派工使直接編輯不安全以前調整資料。

緊急修繕維持電話處理，辦公室保有最終確認權。不得擴張到派工最佳化、付款、承包商 App、API、資料庫、架構、安全設計或 implementation。

Control 與 Treatment 都使用相同八節格式，正規化後分別為 1,926 與 1,898 個字元，避免篇幅成為主要混淆變因：

1. 目標與非目標；
2. 使用者與使用情境；
3. 任務流程；
4. 畫面／wireframe 骨架；
5. 可見資訊、狀態與操作；
6. 錯誤、誤操作與恢復；
7. 角色與權限邊界；
8. 待決策事項與交給後續 Spec 的內容。

## Design round

### Frozen roles

| 身分 | Role ID | Role revision | 責任 | 明確排除 |
| --- | --- | --- | --- | --- |
| 一般 Agent Control | `role-coreplan-maintenance-baseline` | `rolerev-coreplan-maintenance-baseline-r1` | 只依原始任務直接產生 Plan | 不開會、不用 subagent、不看 Treatment／rubric／evaluator |
| Property Maintenance Service Designer | `role-coreplan-maintenance-domain` | `rolerev-coreplan-maintenance-domain-r1` | 產生 task flow、畫面骨架、狀態、操作、錯誤、恢復及 `MNT-UI-*` claims | 不宣稱使用者偏好，不寫技術 Spec 或自創政策 |
| Simulated Tenant Actual User | `role-coreplan-maintenance-tenant` | `rolerev-coreplan-maintenance-tenant-r1` | Phase 1 建立未受方案錨定的 task model；Phase 2 逐項接受、修正或質疑 UI claims | 不做完整替代方案，不設定辦公室政策，不代表真實研究 |
| Main | — | 不算 perspective seat | 建立 claims packet、裁決 authority／scope、綜合並封存 Treatment | 不把模擬使用者意見直接升格為技術或政策權威 |

Design round digest：`15b4c1348034e18a12d059e2178b56845e11434c4905c7bcfe0ed042751e4963`。

### 執行順序

1. 領域專業與模擬租戶分別在 fresh context 做獨立 opening。
2. 專業角色產生 16 個 bounded `MNT-UI-*` claims。
3. 同一位租戶只檢查 claims，不另做整套方案：11 項接受、3 項修正、2 項要求先關閉政策問題。
4. Main 綜合兩者，刪除或收斂超出最低需求的內容，封存 Treatment。
5. Treatment 封存後，才讓 fresh 一般 Agent 只依原始 brief 產生 Control，避免 Control 反向錨定 Main 的 Treatment synthesis。

### Treatment 實際吸收的 End-user 修正

- 「無額外進入說明」不得被理解成允許無人在場時入屋。
- 回覆應表示「此時段可配合」，不能假設填表者本人必然在場。
- 改期送出後必須依已決政策明示原確認是否仍有效，不能默認取消。
- 完整歷史不是租戶端最低必要內容；改為優先顯示現行有效資料與最近一次收件結果。
- 重疊時段是否違規必須由既定政策決定，不能在權威不足時先當成表單錯誤。

## 匿名化與 Review round

兩份 Plan 以 OS randomness 決定 A／B 對照，來源 mapping 在評審完成前不提供給 evaluator：

| 匿名候選 | SHA-256 | 解盲來源 |
| --- | --- | --- |
| Candidate A | `c10e9a653d8b92a4a5044821d9c4f1434fbcf83da9b001251fac520bb00b0869` | 一般 Agent Control |
| Candidate B | `d99d33dcff349d9e793b7524b953e8aedf18935109b94c5385c9cff1f769cf6f` | Main＋專業＋End-user Treatment |

匿名化 manifest digest：`7afcb4e8e3c4d65ee0ee93e60b28540d3fff3bb0b4c4a52ceabcbe996bf6b2e7`。Review round digest：`0161f67ae53bce7f5555f08bc7212bf001a438e5bceb89a7804c43a5d2636323`。

### Fresh evaluator roles

| Role ID | Role revision | 模擬使用者情境 | 主要 lens | 呈現順序 |
| --- | --- | --- | --- | --- |
| `role-coreplan-maintenance-review-taskfit` | `rolerev-coreplan-maintenance-review-taskfit-r1` | 工作與照護時間受限 | 任務符合、自然流程、資訊時機、協調成本 | A → B |
| `role-coreplan-maintenance-review-clarity` | `rolerev-coreplan-maintenance-review-clarity-r1` | 多人同住，填表者與到訪聯絡人可能不同 | 身分、授權、有效資料、誤操作 | B → A |
| `role-coreplan-maintenance-review-recovery` | `rolerev-coreplan-maintenance-review-recovery-r1` | 數位信心較低且操作容易中斷 | 最小任務、死路、中斷與錯誤恢復 | A → B |

每位 evaluator 先只看到任務並封存自己的 unanchored task model，之後才收到匿名候選。他們看不到來源、其他評審輸出、先前實驗結果或預期勝方。

三人使用相同的八個等權 1–5 分維度，可使用 0.5 分：

- 任務符合度；
- 流程自然度；
- 資訊出現時機；
- 狀態與結果清晰度；
- 防止誤操作；
- 恢復是否可執行；
- 範圍簡潔／是否過度設計；
- 是否足以交給下一個 Agent 製作 Spec。

評審不得因技術欄位缺少而扣分，也不得評 API、架構、implementation 或安全工程。

## 盲評結果

### 各 evaluator

| Fresh evaluator | Control A | Treatment B | 差值 | 偏好 | 差距判定 |
| --- | ---: | ---: | ---: | --- | --- |
| 任務與流程 | 4.000 | 4.500 | +0.500 | B | 中等 |
| 清晰度與誤操作 | 3.938 | 4.750 | +0.813 | B | 中等 |
| 簡潔度與恢復 | 4.375 | 4.875 | +0.500 | B | 中等 |
| **合計** | **4.104** | **4.708** | **+0.604** | **B 3、A 0** | **三人皆中等** |

### 維度平均

| 維度 | Control | Treatment | Treatment 差值 |
| --- | ---: | ---: | ---: |
| 任務符合度 | 4.167 | 4.667 | +0.500 |
| 流程自然度 | 4.333 | 4.333 | +0.000 |
| 資訊出現時機 | 4.000 | 4.833 | +0.833 |
| 狀態與結果清晰度 | 3.833 | 4.833 | +1.000 |
| 防止誤操作 | 4.167 | 4.833 | +0.667 |
| 恢復是否可執行 | 4.333 | 4.833 | +0.500 |
| 範圍簡潔／避免過度設計 | 3.833 | 4.500 | +0.667 |
| 後續 Spec handoff | 4.167 | 4.833 | +0.667 |

Treatment 沒有改善自然流程分數；兩者在主要操作順序上都已成熟。差異集中在單一 planner 較容易忽略的「誰、哪份資料、何時生效、失敗後怎麼辦」。這符合本次 skill 假設，而不是泛稱多 Agent 能讓所有面向變好。

## 評審判定的關鍵差異

三位 evaluator 一致認為 Treatment 較好地處理：

1. **有效資料**：畫面持續指出目前有效的時段、聯絡與進入資料，而不只顯示最近編輯內容。
2. **狀態與編輯能力分離**：租戶不會把「不可編輯」誤認為「已確認」或「已取消」。
3. **改期效力**：改期待處理時，原確認是否仍有效必須被明說。
4. **多人實際情境**：填表者、聯絡人與在場者可能不同；「可配合」不等於填表者本人會出現。
5. **進入安全**：進入說明不是無人在場入屋的授權。
6. **競合與恢復**：修改未套用時保留輸入、顯示最新有效資料，並提供重試、提出變更或人工聯絡。
7. **比例原則**：不把完整事件歷史當成核心租戶功能，也不在政策未決時把重疊時段一律判錯。

## 兩個候選的共同缺口

盲評也指出 Treatment 不是完成品：

- 填寫途中離線、關閉頁面或長時間中斷後，草稿是否可恢復仍未明確；
- 帳戶持有人、提交者、聯絡人、在場者及有權批准進入的人仍可再釐清；
- 通知／回覆期限、逾期後果與承包商已被聯絡後的人工變更生效時間，仍需辦公室政策；
- Treatment 的「處理中／結束」若直接作為 UI 狀態仍過於概括；
- 安排進度與編輯能力在規格上應分開，但 UI 不必暴露兩套複雜狀態，應收斂成一個清楚下一步。

這些是進入 Spec 前需要關閉或標記 owner 的問題，不推翻 Treatment 的相對優勢。

## Pilot 流程評估

本次流程 gate 判定為 `PASS`：

- 角色 slate 先展示並由使用者在後續回合確認，沒有同回合預派角色；
- 每個 perspective 與 evaluator 都使用 fresh context；
- End user 在看到任何解法前先完成 unanchored opening；
- End user 第二階段只檢查 bounded claims，沒有取代專業角色做完整方案；
- Treatment 在 Control 以前封存；
- 評審先做 task model，再進行匿名評分；
- 候選格式與長度接近，呈現順序交錯；
- 三位 evaluator 都完成八個維度、證據、排序與差距判定；
- 沒有 retry、replacement、capacity degradation 或 missing role。

因此這套流程可以凍結為後續 N-task 實驗的 baseline protocol。後續任務可以改變角色內容與實際 user lenses，但不應在看完結果後改盲評規則。

## 證據邊界

本 Pilot 支持的是方向性訊號，不是普遍結論：

- 只有一個任務與每個 arm 一次生成，無法分離隨機抽樣效果；
- 專業、模擬使用者與 evaluator 都屬同一 model family；fresh context 提供獨立性，但不是人類或模型多樣性；
- 模擬租戶不是訪談、telemetry、可用性測試或市場證據；
- Main 負責 Treatment synthesis，因此結果也包含 moderator 判斷品質；
- 沒有執行後續 Spec 或 implementation，不能聲稱工程品質已改善；
- 分數偏高，仍可能存在 ceiling effect；
- 沒有量測 token、延遲或金錢成本。

合理表述是：「這個 Pilot 顯示，加入一位 bounded 領域專業與一位先 opening、再 critique 的模擬 End user，可能實質改善 Plan 的使用者現實性、狀態清晰度、恢復與比例原則。」不應表述為「meeting skill 已被證明普遍有效」。

## N-task 正式實驗建議

下一步先凍結本流程，再跑至少 6 個新任務：

| 任務類型 | 建議數量 | 用途 |
| --- | ---: | --- |
| 小型、單一主要操作員、低後果 | 2 | 良性負向對照；檢查 skill 是否不必要地增加複雜度 |
| 小型、兩種以上實際參與者或交接 | 2 | 檢查身分、資訊時機與 handoff 改善 |
| 中小型、狀態變更會造成實體或營運後果 | 2 | 檢查有效資料、誤操作與恢復改善 |

每案保持：

- Control 為 fresh 一般 Agent，只看原始 brief；
- Treatment 預設為 Main＋一位領域專業＋一至兩位 evidence-distinct End-user lenses；
- 技術角色不預設加入 Plan 討論，除非技術可行性本身就是已知產品限制；
- 只評 Plan，不跑 Spec 或 implementation；
- 兩份 Plan 使用相同格式與相近長度；
- 三位新的 simulated End-user evaluators 先 opening、再盲評；
- 保留正向、中性與負向結果，不因單案輸掉就修改 rubric。

正式批次應同時報告：逐案勝負、八維度平均、是否降低過度設計、角色與 invocation 成本，以及哪些任務沒有受益。若小型低後果任務多為平手，而多參與者／高誤操作後果任務穩定提升，這會是比「全部任務平均變好」更可信也更有產品價值的適用邊界。

## 對既有報告的定位

先前三份報告仍有價值，但它們主要評估包含 domain state、API、race、recovery、rollout 與 technical contracts 的完整 plan／spec，以及 Large／Compact 席位和 synthesis 形式。它們適合用來回答「技術型 meeting 怎麼避免過度拆席與失真」，不應再作為 clarified core claim 的直接證據。

本報告才是下列主張的第一份直接 Pilot 證據：

> meeting skill 先改善使用者任務與 UIUX Plan，再把較好的 Plan 交給普通 Agent 進入後續 Spec 流程。

舊報告保留為次要、歷史與機制性證據；正式核心證據仍需完成上述 N-task 批次。

## Completion receipt

- `planrev-core-plan-maintenance-design-r1`：2/2 Treatment perspective roles completed；Tenant role 完成兩階段；Baseline role completed；Main synthesis completed。
- `planrev-core-plan-maintenance-review-r1`：3/3 evaluator roles 完成兩階段 blind review。
- Retry／replacement／degradation：none。
- Missing planned roles：none。
- Design artifact mapping：Control = Candidate A；Treatment = Candidate B。
- Pilot protocol：`PASS`。
- 單案方向性品質訊號：`POSITIVE`；Treatment 3–0、平均 `+0.604/5`。
- 產品有效性結論：`PENDING_N_TASK_VALIDATION`。
