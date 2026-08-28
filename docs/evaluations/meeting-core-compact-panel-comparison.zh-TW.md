# Meeting core 3–4 人 compact panel 規劃品質評估

- 評估日期：2026-08-29
- 評估範圍：GUI 實作前的 plan／spec 品質，不是 implementation 品質
- 狀態：三案 compact meeting 與 fresh blind review 已完成
- 前次實驗：[Meeting core 規劃品質對照評估](meeting-core-quality-comparison.zh-TW.md)

## 結論摘要

把 meeting 的總席位壓到 3–4 人後，三個任務都勝過完全相同的一般-session baseline：

| 任務 | 一般 session | Compact meeting | 差值 | Judges 偏好 | 實務差距 |
| --- | ---: | ---: | ---: | --- | --- |
| 候補名單自動遞補 | 4.167 | 4.625 | +0.458 | compact 3、一般 0 | 1 小幅、2 中等 |
| 出貨前修改地址 | 4.000 | 4.667 | +0.667 | compact 3、一般 0 | 1 中等、2 大幅 |
| CRM CSV 聯絡人匯入 | 4.208 | 4.625 | +0.417 | compact 3、一般 0 | 3 中等 |
| **三案合計** | **4.125** | **4.639** | **+0.514** | **compact 9、一般 0** | — |

前次 7／8／4 席 meeting 只有候補名單勝出；地址與 CSV 都略輸一般 session。本輪 4／4／3 席則保留候補名單的提升，並把另外兩案反轉為一致勝出。

這份證據支持的不是「角色越少越好」，而是：對這類中小型規劃，保留真正不同的使用者視角、合併可由同一人閉合的專業責任，可能比拆出多個 architecture／security／reliability specialists 更有效。壓縮降低了彼此新增狀態與政策、最後卻無法關閉的風險。

代價也很明確：compact plans 的資訊密度仍不足。三案在 `concision_signal` 都從一般 session 的 5.000 降到 3.000。它們贏在狀態一致性、失敗恢復與 policy discipline，不是贏在篇幅或成本。

## 評估問題

在任務、一般-session baseline、模型條件、評分維度與 blind-review protocol 不變時，把 meeting 總席位限制在 3–4 人，能否保留或改善原本多視角規劃的品質，同時降低角色過度拆分？

本輪主要檢查三件事：

1. 候補名單原有的正向效果是否保留；
2. 地址變更是否不再因 specialist seats 各自擴大 state machine 而失分；
3. CSV 這類有界任務是否仍然沒有價值，或聚焦後能找到一般 session 遺漏的具體風險。

## 控制方式

三案沿用前次實驗完全相同的任務 brief 與一般-session 產出，不重新抽樣 baseline。這樣可以把新增變因集中在 meeting slate 與 synthesis，而不是一般 planner 的隨機差異。

每案流程：

1. Main 依目前 skill 產生一份 3–4 人完整角色 slate；
2. 使用者看到完整角色定義後，明確確認 `planrev-compact-waitlist-r1`、`planrev-compact-address-r1`、`planrev-compact-csv-r1`；
3. 角色 freeze 後，以 fresh independent contexts 執行；角色看不到 baseline、評分規則、預期修正、其他角色輸出或舊實驗結果；
4. simulated actual-user role 先做 unanchored task model，再只針對專業角色公開的 bounded UI claims 執行第二階段 critique；
5. Main 綜合公開 findings，刪除重複或無 authority 的提案，產出 compact plan；
6. 三位新的 fresh judges 盲評匿名配對；候選位置在不同任務交錯，避免以 A／B 位置猜來源。

評分維度與前次相同，皆為 1–5 分：

- `requirements_coverage`
- `multi_user_workflow`
- `domain_state_consistency`
- `failure_recovery`
- `implementability_contracts`
- `ui_operability`
- `scope_assumption_discipline`
- `concision_signal`

Judges 被明確要求不得因篇幅、複雜度、章節數或表面工作量加分；無 authority 的政策、矛盾、過度設計、模糊 contract 與沒有 exit 的狀態都必須扣分。

## 角色 slate 與結構性成本

| 任務 | Range | Compact slate | 前次席位 | 本次席位 | 降幅 |
| --- | --- | --- | ---: | ---: | ---: |
| 候補名單 | `standard` | 候補容量／服務 generalist；公開客戶；第一線行事曆；CMS 營運 | 7 | 4 | 42.9% |
| 地址變更 | `standard` | 訂單地址／履約 generalist；購買客戶；倉儲；CMS 客服 | 8 | 4 | 50.0% |
| CSV 匯入 | `lightweight` | CRM import generalist；資料正確性／恢復；Workspace Admin | 4 | 3 | 25.0% |
| **合計** | — | — | **19** | **11** | **42.1%** |

壓縮集中在專業角色；三案的 3／3／1 個 simulated actual-user seats 都保留。這符合本次假設：同一個 generalist 可以同時負責架構、狀態、相容與基本 reliability，但不能取代真正操作或承受流程結果的人。

席位數不等於實際 model invocation 數。Actual-user protocol 有 opening 與 bounded critique 兩階段，因此本輪 11 個 frozen seats 共產生 18 次 perspective turns：候補 7、地址 7、CSV 4。Main 的 slate 產生、綜合與 judges 也不計入 meeting headcount。報告沒有把 42.1% 席位降幅誤寫成 token、延遲或金錢降幅。

## 盲評結果

### 維度平均

下表為三任務、三位 judges 的平均；每個欄位都有相同樣本數。

| 維度 | 一般 session | Compact meeting | 差值 |
| --- | ---: | ---: | ---: |
| 需求覆蓋 | 4.333 | 5.000 | +0.667 |
| 多使用者工作流 | 4.444 | 4.889 | +0.445 |
| Domain／state 一致性 | 3.889 | 5.000 | +1.111 |
| 失敗恢復 | 4.000 | 5.000 | +1.000 |
| Contract 可實作性 | 4.000 | 4.333 | +0.333 |
| UI 可操作性 | 4.111 | 5.000 | +0.889 |
| Scope／假設紀律 | 3.222 | 4.889 | +1.667 |
| 精簡度／資訊密度 | 5.000 | 3.000 | -2.000 |

最明顯的改善不是增加更多功能，而是把 authority、state、retry 與 policy boundary 說清楚。最明顯的退步則是篇幅與協調成本；這是下一輪應優化的主因。

### 候補名單：保留原本優勢

4 人方案仍把 booking/calendar capacity 當成唯一容量 authority，另外分開：

- 候補需求；
- 邀請或 capacity lease 的業務權利；
- 不可靠的通知投遞 attempts。

客戶視角要求把 `waiting`、`action required`、`booked`、`expired`、`withdrawn` 與具名分店時區說清楚；第一線視角要求 stale 或矛盾狀態不可操作，且衝突後要有可對客說明與 escalation；CMS 視角要求 activation 顯示每個 policy 的來源、scope、precedence 與版本。

三位 judges 都偏好 compact。一般 baseline 雖然精簡且可實作，但直接採用 FIFO、30 分鐘、逾期失去順位與 staff precedence，後面又把它們列成待決策事項。Compact plan 把這些改成 activation 前的 versioned decisions，並為 race loss、delivery failure、revocation 與 reconciliation 提供 exit。

需改善：同時描述 lease 與 no-lease 分支，增加了首版負擔。真正進 implementation spec 前應由產品決定一條路，刪掉另一半 contract。

### 地址變更：從負向反轉為最大提升

這案最能支持壓縮策略。前次大型 meeting 把多個 specialist 提出的狀態與 carrier／HOLD 政策疊在一起，最後 `applied` 同時混合地址 authority 與履約／標籤收斂，造成內部不閉合。

本輪由一個 generalist 統一設計：

- immutable address revisions；
- 訂單唯一 authoritative pointer；
- address-change request；
- 只在必要時存在、且不改寫 order state 的 fulfillment gate；
- 永遠不是地址 authority 的 generation-scoped carrier label。

`APPLIED` 被限定為 authoritative pointer 已切換，而且這次變更要求的實體／標籤 reconciliation 已完成。客戶、倉儲、CMS 三個視角再分別補上「收到請求不等於已套用」、「stale printed label 不能繼續出貨」、「generic override 在 authority 未定前不得出現」。

三位 judges 一致認為一般 baseline 在 `label_created` 直接拒絕改址，沒有完整涵蓋題目所稱的出貨前；compact plan 雖然明顯更重，但能安全處理 replacement、old-label retirement、out-of-order callback 與 physical artifact mismatch，因此形成全案最大差值。

需改善：scan evidence、fine-grained capability 與 reconciliation queue 可能超出小型商店首個 pilot。Implementation spec 應先查現有倉儲 runtime，刪除沒有實際 writer／artifact 的控制，不要因評估 plan 完整就全數建置。

### CSV 匯入：有界任務也得到提升，但不是免費提升

前次結果顯示 meeting 對 CSV 沒有明顯效益。本輪保留一個 product/application generalist，只額外拆出 data correctness/recovery，並由唯一主要使用者 Workspace Admin 驗證 UI。

改善集中在具體 contract：

- importer 必須重用既有 CRUD normalization／validation authority；
- 若 runtime 無法證明 workspace email unique，update/upsert 不啟用；不以 name、phone、company 或 tags 猜 identity；
- preview 與 final results 的互斥 counts 必須與每一 source row 對帳；
- retry 不能重播 finalized rows，修正資料或 mapping 必須建立新的 manifest revision；
- rollback 是 dry-run 後的 conditional compensation，不能覆蓋後續編輯或破壞 references。

三位 judges 都偏好 compact，主要原因是一般 baseline 一方面直接採電話 fallback matching、tag auto-create、7 天 retention／rollback window，另一方面又把這些列為未決政策；retry conflict rows 與 row-state reconciliation 也較模糊。

但這仍是良性警告，不代表小型 CSV 匯入一定要開 meeting。Compact 方案加入 durable manifest 與完整 compensation，實作面積比一般 baseline 大；若產品接受「不提供 bulk rollback，只提供結果 manifest 與手動修復」，3 人 panel 的部分優勢會下降。這案證明 focused panel 可以找到風險，不證明其成本永遠划算。

## 與前次大型 meeting 的方向比較

| 任務 | 前次大型 meeting 相對一般 | 本次 compact 相對同一一般 baseline | 方向 |
| --- | --- | --- | --- |
| 候補名單 | +0.416；skill 3–0 | +0.458；compact 3–0 | 正向保留 |
| 地址變更 | -0.167；skill 1–2 | +0.667；compact 3–0 | 負向反轉 |
| CSV 匯入 | -0.125；skill 0–2、平手 1 | +0.417；compact 3–0 | 負向反轉 |

兩輪 judges 都是 fresh，但不是同一批人；前次與本次絕對分數不可當作直接 A/B。可比較的是：兩輪都使用同一 baseline 作為各自的匿名 anchor，而方向與 judges 一致性發生明顯變化。若要把「4 人必然優於 8 人」建立成更強因果結論，仍需由同一批 fresh judges 直接盲評 large-vs-compact，並增加更多任務。

## 對 meeting core 與 GUI 的建議

### 建議採用

1. **中小型 `lightweight`／`standard` 任務，Main 預設先提出 3–4 席最小充分 slate。** 這是建議起點，不是 schema hard cap。
2. **優先保留 actual-user seats，從專業席開始合併。** 一個能負責 product/domain/application/reliability 的 generalist，通常比四個各自新增局部狀態的 specialists 更容易產生閉合 plan。
3. **只有 evidence、authority 或 failure consequence 真正不同時才拆 specialist。** CSV 的 data/recovery 是合理拆分；一般 security 或 architecture concern 本身不是獨立席理由。
4. **Main 在 role review 顯示 headcount 與預估 perspective turns。** GUI 不應把「4 人」包裝成「只會呼叫 4 次」。Actual-user 二階段與 re-review 都有額外成本。
5. **Synthesis 新增 compression pass。** 最終輸出前要求 Main 刪除未被採用的替代分支、重複狀態、沒有 runtime evidence 的控制，以及只有 observability 沒有 recovery owner 的內容。
6. **以 closure gate 判定會議品質，不以每個部門都有建議判定。** 每個關鍵 state 必須有 authority、owner、exit；每個 UI success claim 必須對應 committed domain fact；未決政策必須有 decision owner 與 activation gate。

### 不建議直接採用

- 不把 3–4 人寫成所有任務的固定限制；critical identity、finance、regulated data、irreversible migration 或 public-contract 任務仍可能需要更多 evidence-distinct seats。
- 不因本次三案全勝就宣稱 meeting 對小任務普遍有效；本輪 plans 仍有明顯 verbosity 與實作面積成本。
- 不移除 actual-user critique 來節省 calls。這次多個高價值修正都出現在 phase 2，而不是專業角色第一次提案。
- 不用加權投票取代 evidence／authority adjudication。席位壓縮的價值正是降低票數與角色權重對結論的扭曲。

## 建議通過標準

一案不以「每個角色都提出有效建議」作為主要通過條件，而應同時滿足：

- confirmed slate 的高風險 surface 沒有遺漏；
- 每個採用項目能指出 task evidence 或 authority，沒有用角色聲量取代證據；
- 所有 nonterminal state 都有 owner、exit、timeout／retry 或 escalation；
- concurrency winner/loser 與 idempotent replay 有穩定結果；
- actual-user critique 提出的 UI 修正已接受、拒絕或明確 deferred；
- 未決商業政策有 decision owner 與阻擋點，不被包成 implementation default；
- synthesis 已移除互相矛盾、重複或不成比例的提案；
- plan 的實作順序、compatibility、tests、observability 與 recovery 可以彼此對帳。

Compact panel 另外增加一個成本 gate：若它相對一般 planner 的主要新增內容只有更多資料表、狀態、queue 與 dashboard，而沒有填補 authority、user consequence 或 failure exit，則不應視為品質提升。

## 限制

- 只有三個任務與一個 model family。
- Judges 評的是 plan／spec，不是實作或 production outcome。
- Actual-user roles 是模擬視角，不能取代訪談、可用性測試或 telemetry。
- 本次重用 baseline，可控制 planner variance；但前次與本次 judge cohorts 不同，不能直接比較絕對分數。
- 沒有用同一批 fresh judges 直接執行 large-vs-compact pairwise review。
- 沒有量測 token、wall-clock、latency 或金錢；席位與 perspective turns 只是結構性成本。
- Compact plans 明顯較長；judges 雖已對 concision 扣分，仍可能存在「完整 contract」偏好。
- 地址與 CSV 的部分優勢來自比 baseline 更嚴格地拒絕無 authority 政策，effect size 不應外推到規則已成熟的產品。

## 最終判斷

本輪證據足以支持把「3–4 席最小充分 slate」帶進 GUI 設計，作為中小型任務的建議預設；也支持保留使用者可調整人數與角色的能力。

它尚不足以支持 hard cap，也不足以說多視角在小任務必然值得。下一個核心優化不再是增加角色，而是讓 Main 更積極壓縮 synthesis：保留本輪 state／authority／recovery 的品質，同時把 `concision_signal` 從 3 拉回接近一般 session 的 5。
