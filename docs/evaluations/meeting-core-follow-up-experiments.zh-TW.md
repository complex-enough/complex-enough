# Meeting core 後續控制實驗：席位、壓縮與 actual-user ablation

- 評估日期：2026-08-30
- 評估範圍：GUI 實作前的 plan／spec 品質；不評 implementation 品質
- 狀態：三組實驗與 fresh blind review 全部完成
- 前置報告：[3–4 人 compact panel 規劃品質評估](meeting-core-compact-panel-comparison.zh-TW.md)
- 凍結 revisions：`evalrev-large-vs-compact-r1`、`evalrev-synthesis-compression-r1`、`planrev-address-user-ablation-r1`

## 結論摘要

三組實驗支持四個不同層次的結論：

1. **3–4 人 Compact 並不是因為換了一批 judges 才顯得較好。** 在同一批新的盲評者直接比較 Large 與 Compact 時，Compact 三案均勝，偏好為 9–0，平均分高 `+0.347`。
2. **Compact 的主要剩餘問題確實是 synthesis，不是再加角色。** 把完整 Compact plan 壓到原字數的 35–38% 後，品質仍高，但完整版以 6–3 勝出，平均只領先 `0.066`。Uniform aggressive compression 已開始刪到例外、恢復 owner 與 implementability contract。
3. **Actual-user coverage 有效，但不是人越多越好。** 一個刻意人工合併的 customer／warehouse／CMS 角色取得最佳整體平衡；三個拆開的 actual-user roles 把需求、多使用者流程與 UI 操作性拉到最高，卻也使 synthesis 把部分現場疑慮誤升格為過重或矛盾的技術 invariant。
4. **Actual-user finding 應作為 failure consequence／UI claim 的挑戰證據，不是技術 authority。** Main 必須接受其指出的後果，再交回專業 contract 驗證；不能把使用者提出的「所有舊標都要消失」直接寫成不可證明的系統承諾。

因此目前較合理的 meeting core 主軸是：

- 中小型任務先採 3–4 席、小而不同的 lenses；
- actual-user roles 依實際權限、工作與失敗後果選擇，不固定拆成每個 surface 一席；
- Main 對人數與拆分提供建議，使用者可調整；
- synthesis 使用 layered compression：主文件保留 authority、states、主要 races、recovery owners 與 actor outcomes，把完整 anomaly inventory、欄位表與 observability 細節移到附錄，而不是一律刪到 35–38%。

## 實驗一：Large vs Compact 同批直接盲評

### 問題與控制

本實驗補上前兩輪最大的比較缺口：Large meeting 與 Compact meeting 先前各自對一般 session 評分，但 judges 不同，不能直接推論 Compact 優於 Large。

三案沿用原任務與既有兩份 meeting plan，重新匿名交錯候選位置；三位新評審在 fresh context 中直接比較。評審不知道席位數、來源、舊成績或預期結論，也不得因長度、章節數、技術密度或語言加分。

來源語言保留為原始繁中／英文，評審被要求在評分時做等義語意 normalization，語言流暢度不得計分。這不是逐句翻譯，仍列為限制。

### 結果

| 任務 | Large | Compact | Compact 差值 | 盲評偏好 |
| --- | ---: | ---: | ---: | --- |
| 候補名單自動遞補 | 4.521 | 4.813 | +0.292 | Compact 3、Large 0 |
| 出貨前修改地址 | 4.521 | 4.771 | +0.250 | Compact 3、Large 0 |
| CRM CSV 聯絡人匯入 | 4.229 | 4.729 | +0.500 | Compact 3、Large 0 |
| **合計** | **4.424** | **4.771** | **+0.347** | **Compact 9、Large 0** |

### 維度平均

| 維度 | Large | Compact | 差值 |
| --- | ---: | ---: | ---: |
| 需求覆蓋 | 4.556 | 5.000 | +0.444 |
| 多使用者工作流 | 4.444 | 4.889 | +0.445 |
| Domain／state 一致性 | 4.333 | 4.944 | +0.611 |
| 失敗恢復 | 4.111 | 5.000 | +0.889 |
| Contract 可實作性 | 4.333 | 4.944 | +0.611 |
| UI 可操作性 | 4.500 | 5.000 | +0.500 |
| Scope／假設紀律 | 4.222 | 4.833 | +0.611 |
| 精簡度／資訊密度 | 4.889 | 3.556 | -1.333 |

Compact 的改善集中在 authority、state closure、failure exit、policy gate 與 actor-visible outcome；代價仍然是篇幅。CSV 差距最大，表示前次「小型任務可能沒有明顯效益」不能概括成「CSV 不適合 meeting」；較準確的說法是：有界任務需要更少但真正不同的 lenses，尤其 identity／rollback consequence 與 Admin operability。

## 實驗二：完整 synthesis vs 35–38% 壓縮版

### 問題與控制

Main 以三份完整 Compact plans 為唯一來源，建立同結論壓縮版。壓縮版沒有加入新 finding，保留目標／非目標、authority／invariants、核心 state、三面流程、policy gates、API／events、主要競態／恢復、相容性、rollout、tests 與 implementation order；刪除重複 rationale、展開式 anomaly inventory、部分欄位及運維細節。

字數比例：候補 `671/1864 = 36.0%`、地址 `712/2013 = 35.4%`、CSV `656/1728 = 38.0%`。完整／壓縮位置每案交錯，三位 judges 使用新的 context。

### 結果

| 任務 | 完整版 | 壓縮版 | 壓縮版差值 | 偏好 |
| --- | ---: | ---: | ---: | --- |
| 候補名單 | 4.833 | 4.750 | -0.083 | 完整 2、壓縮 1 |
| 地址修改 | 4.854 | 4.792 | -0.063 | 完整 2、壓縮 1 |
| CSV 匯入 | 4.792 | 4.740 | -0.052 | 完整 2、壓縮 1 |
| **合計** | **4.826** | **4.760** | **-0.066** | **完整 6、壓縮 3** |

| 維度 | 完整版 | 壓縮版 | 壓縮差值 |
| --- | ---: | ---: | ---: |
| 需求覆蓋 | 5.000 | 4.861 | -0.139 |
| 多使用者工作流 | 5.000 | 4.722 | -0.278 |
| Domain／state 一致性 | 4.889 | 4.806 | -0.083 |
| 失敗恢復 | 5.000 | 4.611 | -0.389 |
| Contract 可實作性 | 5.000 | 4.500 | -0.500 |
| UI 可操作性 | 5.000 | 4.583 | -0.417 |
| Scope／假設紀律 | 4.833 | 5.000 | +0.167 |
| 精簡度／資訊密度 | 3.889 | 5.000 | +1.111 |

結果不是「不能壓縮」。壓縮版平均仍有 4.760，且 scope／資訊密度明顯較好；但 35–38% 已超過三案共同的安全壓縮邊界，最先流失的是：

- conditional mode 的精確語意，例如 lease／no-lease 對客戶承諾的差異；
- recovery owner、例外偵測與 reconciliation output；
- 10k synchronous fallback、retention-expiry retry、compensation classification；
- physical label retirement 與 carrier uncertainty 的交接細節。

三位 reviewer 的分歧也有意義：Contract 與 Operability reviewers 三案都選完整版；Scope/Handoff reviewer 三案都選壓縮版。合理產品化方向不是固定輸出一個長度，而是產生：

1. 主 plan：必須能閉合 authority、state、top races、recovery owner、actor outcome；
2. 附錄：完整 race matrix、欄位／reason code、anomaly inventory、observability；
3. Main 在收尾時刪除重複敘述，但不能只按比例裁切。

本實驗沒有從原始 issue ledger 分別重新 synthesis；它評的是既有最終方案的 editorial compression，因此不能推論「較短的會議過程」會得到相同結果。

## 實驗三：Actual-user 角色 ablation

### 問題與控制

地址修改任務同時有 customer、warehouse 與 legacy CMS 三個 materially different surfaces，且前兩輪結果反轉最明顯，因此用來檢查 actual-user role granularity。

一位 professional generalist 先產生唯一且凍結的 domain/state/API/carrier skeleton 與 12 個 `ABL-A-UI-*` public claims。三個 arms 使用完全相同的專業產物：

| 盲評代號 | 實驗組 | 可使用的 user evidence | 字數 |
| --- | --- | --- | ---: |
| `alpha` | Composite user | 一位刻意人工合併的 customer＋warehouse＋CMS opening／critique | 801 |
| `beta` | Split users | customer、warehouse、CMS 三位各自 opening／critique | 804 |
| `gamma` | Professional only | 不使用 actual-user finding | 829 |

所有 user roles 先做 unanchored task model，再只看與自身 surface 有關的 bounded claims。它們不看 generalist 原始報告、不看彼此 finding，也不能決定架構、policy 或實際偏好。Main 以同結構與近似篇幅整合三個匿名版本。

### 結果

| Arm | 平均 | 三位排序 | 第一名次數 | 結果特徵 |
| --- | ---: | --- | ---: | --- |
| Composite (`alpha`) | **4.688** | 1、2、1 | **2** | 整體平衡最好 |
| Split (`beta`) | 4.458 | 2、1、3 | 1 | UI／多使用者最高，技術比例性下降 |
| Professional only (`gamma`) | 4.458 | 3、3、2 | 0 | scope／技術交接較穩，使用者後果較薄 |

| 維度 | Composite | Split | Professional only |
| --- | ---: | ---: | ---: |
| 需求覆蓋 | 4.833 | **5.000** | 4.500 |
| 多使用者工作流 | 4.833 | **5.000** | 4.000 |
| Domain／state 一致性 | **4.333** | 3.667 | **4.333** |
| 失敗恢復 | **4.667** | **4.667** | 4.500 |
| Contract 可實作性 | **4.500** | 4.000 | **4.500** |
| UI 可操作性 | 4.833 | **5.000** | 4.000 |
| Scope／假設紀律 | 4.667 | 4.000 | **5.000** |
| 精簡度／資訊密度 | **4.833** | 4.333 | **4.833** |

### 如何解讀

Split users 找到 professional-only 明顯漏掉的 consequence：

- customer 必須持續分辨 received、approved、applied，並知道目前權威地址與失敗後是否仍可能寄往舊址；
- warehouse 不只需要數位 gate，還要處理已列印標籤、實體包裹、最後交運檢查與人工流程；
- CMS 必須看到可信 actor、責任 queue、evidence 與具名 authority，不能有 generic override。

Operability reviewer 因此把 Split 排第一。但 Main 若把這些後果直接編譯成 hard implementation rules，會出現新的問題：

- 「必須消除每一張舊標籤」不可完整證明，應改成追蹤所有已知 artifact、隔離與 exception evidence；
- hold 阻擋普通 label creation，同時又要求 replacement label 才能解除，若沒有 reconciliation-only command／gate substate 就會 deadlock；
- user role 要求的 final handoff scan 可能是安全 control，也可能是超出現有流程的重大改造，需由 warehouse authority／runtime evidence 決定。

Composite 角色反而較常把 finding 保持在 outcome 與 handoff 層：區分 actor vocabulary、標明 parcel scope、說明 stale action 沒有造成進度、具名 recovery owner／authority；它沒有把每個 surface 的最大安全要求全部堆進方案，因此整體平衡最好。

這不證明 composite 永遠優於 split roles。它證明的是：

- actual-user 拆席能提高 finding recall；
- Main moderation／反向傳播能力決定這些 findings 是否提升 final plan；
- 對中小型任務，拆成三席後必須再做 conflict／proportionality pass，否則更多有效意見仍可能造成 contract 過度收緊；
- 同一專業有幾個 actual-user seats，應由不同權限、evidence 與 failure consequence 決定，而不是介面數量。

### 共同技術 finding

三個 arms 都繼承一個 professional skeleton 缺口：一般 label creation 被 hold 阻擋，但 applied 又可能要求 replacement label。實作前必須明定一個受限的 reconciliation-only label command、gate substate，或其他不重新開放普通履約的 path。這是 `PASS_WITH_CHANGES` 條件，不能因 user-role 組合不同而忽略。

## Confirmed roles 與執行紀錄

### 實驗一 evaluator slate

| Role revision | Department | 主要 ownership | 結果 |
| --- | --- | --- | --- |
| `rolerev-e1-contract-state-recovery-auditor-r1` | System Assurance | authority、state、race、recovery、implementability | completed，wave 1，無 degradation |
| `rolerev-e1-multi-user-operability-auditor-r1` | Workflow & Usability Assurance | actor flow、資訊時機、misoperation、recovery UX | completed，wave 1，無 degradation |
| `rolerev-e1-scope-handoff-auditor-r1` | Delivery Assurance | scope、比例性、資訊密度、handoff | completed，wave 1，無 degradation |

### 實驗二 evaluator slate

| Role revision | Department | 主要 ownership | 結果 |
| --- | --- | --- | --- |
| `rolerev-e2-contract-state-recovery-auditor-r1` | System Assurance | 壓縮後的 authority／state／recovery closure | completed，wave 1，無 degradation |
| `rolerev-e2-multi-user-operability-auditor-r1` | Workflow & Usability Assurance | 壓縮後的 actor consequence／UI operability | completed，wave 1，無 degradation |
| `rolerev-e2-scope-handoff-auditor-r1` | Delivery Assurance | 壓縮比例、重複、交接品質 | completed，wave 1，無 degradation |

### 實驗三 content slate

| Role revision | Department／type | 執行階段／wave | Material contribution |
| --- | --- | --- | --- |
| `rolerev-ablation-address-generalist-r1` | Product & Fulfillment Engineering | professional opening，wave 1，completed | 唯一 authority/request/gate/label/CAS skeleton 與 12 個 public UI claims |
| `rolerev-ablation-address-composite-user-r1` | Experimental Simulated Actual-User Lens | opening wave 1；critique wave 4；completed | actor vocabulary、scope、recovery owner、跨角色 handoff；明示 artificial merge 限制 |
| `rolerev-ablation-address-customer-r1` | Customer Operations／simulated user | opening wave 1；critique wave 4；completed | received/approved/applied、當前地址、競態／政策 consequence、最終補救 |
| `rolerev-ablation-address-warehouse-r1` | Warehouse Operations／simulated user | opening wave 2；critique wave 4；completed | printed artifacts、package、handoff、manual path、physical recovery |
| `rolerev-ablation-address-cms-r1` | Customer Support Operations／simulated user | opening wave 3；critique wave 5；completed | trusted actor、authority/evidence、responsible queue、no generic override |

### 實驗三 evaluator slate

| Role revision | Department | 主要 ownership | 結果 |
| --- | --- | --- | --- |
| `rolerev-e3-contract-state-recovery-auditor-r1` | System Assurance | 三 arms 的 technical closure | completed，review wave 6，無 degradation |
| `rolerev-e3-multi-user-operability-auditor-r1` | Workflow & Usability Assurance | 三面 task／UI／physical consequence | completed，review wave 6，無 degradation |
| `rolerev-e3-scope-handoff-auditor-r1` | Delivery Assurance | 比例性、交接、過度設計 | completed，review wave 6，無 degradation |

Main 為 moderator／synthesizer，不計為 perspective seat。所有 content openings 與 evaluator openings 使用 fresh contexts；actual-user critique 是同一 frozen role 的第二階段，不是新增角色或投票。

## Public evidence ledger

| Item | Disposition | 結論 | Source role revisions | Public locator |
| --- | --- | --- | --- | --- |
| `EXP1-COMPACT-DIRECT` | accepted | Compact 在同批直接比較三案皆勝，偏好 9–0 | `rolerev-e1-contract-state-recovery-auditor-r1`、`rolerev-e1-multi-user-operability-auditor-r1`、`rolerev-e1-scope-handoff-auditor-r1` | 實驗一結果／維度表 |
| `EXP1-CONCISION-RISK` | accepted residual risk | Compact 的主要一致性代價仍是篇幅與資訊密度 | `rolerev-e1-contract-state-recovery-auditor-r1`、`rolerev-e1-multi-user-operability-auditor-r1`、`rolerev-e1-scope-handoff-auditor-r1` | 實驗一維度表 `concision_signal` |
| `EXP2-FULL-EDGE` | accepted | 35–38% 壓縮後完整版以 6–3、平均 +0.066 小幅領先 | `rolerev-e2-contract-state-recovery-auditor-r1`、`rolerev-e2-multi-user-operability-auditor-r1` | 實驗二結果表 |
| `EXP2-COMPRESSION-VALUE` | accepted minority | 壓縮版仍高品質，scope／concision 更好；可用 selective compression | `rolerev-e2-scope-handoff-auditor-r1` | 實驗二維度表與 reviewer split |
| `EXP3-COMPOSITE-BALANCE` | accepted | Composite arm 整體平均最高、三位中兩位排第一 | `rolerev-e3-contract-state-recovery-auditor-r1`、`rolerev-e3-scope-handoff-auditor-r1` | 實驗三結果表 |
| `EXP3-SPLIT-OPERABILITY` | accepted minority | Split arm 的 requirements／multi-user／UI 最高，Operability reviewer 排第一 | `rolerev-e3-multi-user-operability-auditor-r1` | 實驗三維度表 |
| `EXP3-SPLIT-OVERCOMPILE` | accepted | 未經 authority back-propagation 時，split findings 可被誤編譯成矛盾或不可證明 contract | `rolerev-e3-contract-state-recovery-auditor-r1`、`rolerev-e3-scope-handoff-auditor-r1` | 實驗三如何解讀 |
| `EXP3-PROFESSIONAL-TRADEOFF` | accepted | Professional-only 的 scope discipline 最高，但 multi-user／UI 明顯較薄 | `rolerev-e3-contract-state-recovery-auditor-r1`、`rolerev-e3-multi-user-operability-auditor-r1`、`rolerev-e3-scope-handoff-auditor-r1` | 實驗三維度表 |
| `EXP3-GENERALIST-SKELETON` | accepted input | 共用 professional skeleton 建立唯一 address authority、request／gate／label／CAS 與 12 個 UI claims | `rolerev-ablation-address-generalist-r1` | 實驗三問題與控制／共同技術 finding |
| `EXP3-COMPOSITE-HANDOFF` | accepted input | Composite finding 保留 actor vocabulary、parcel scope、stale-action consequence 與 recovery owner | `rolerev-ablation-address-composite-user-r1` | 實驗三如何解讀 |
| `EXP3-CUSTOMER-OUTCOME` | accepted input | Customer 必須分辨 received／approved／applied、目前權威地址、競態與最終補救 | `rolerev-ablation-address-customer-r1` | 實驗三如何解讀 |
| `EXP3-WAREHOUSE-PHYSICAL` | accepted input | Warehouse finding 補出 printed artifact、package、handoff 與 manual-path consequence | `rolerev-ablation-address-warehouse-r1` | 實驗三如何解讀 |
| `EXP3-CMS-AUTHORITY` | accepted input | CMS finding 要求 trusted actor、具名 authority/evidence、責任 queue 且拒絕 generic override | `rolerev-ablation-address-cms-r1` | 實驗三如何解讀 |
| `EXP3-LABEL-DEADLOCK` | accepted high | hold 與 replacement-label path 未閉合，三 arms 實作前都需修正 | `rolerev-ablation-address-generalist-r1`、`rolerev-e3-contract-state-recovery-auditor-r1`、`rolerev-e3-multi-user-operability-auditor-r1`、`rolerev-e3-scope-handoff-auditor-r1` | 實驗三共同技術 finding |
| `CLAIM-MORE-USERS-ALWAYS-BETTER` | rejected | 三席提升 recall，不等於 final plan 整體品質必然較高 | `rolerev-e3-contract-state-recovery-auditor-r1`、`rolerev-e3-multi-user-operability-auditor-r1`、`rolerev-e3-scope-handoff-auditor-r1` | 實驗三排序／維度 |
| `CLAIM-LONGER-ALWAYS-BETTER` | rejected | Scope reviewer 三案皆選壓縮；完整版只小幅領先 | `rolerev-e2-contract-state-recovery-auditor-r1`、`rolerev-e2-multi-user-operability-auditor-r1`、`rolerev-e2-scope-handoff-auditor-r1` | 實驗二結果／reviewer split |

## 限制

1. 三組實驗都使用內部 simulated perspectives，不是真實使用者研究。
2. E1／E2 只有三個中小型任務；E3 只跑地址修改一案，不能直接外推所有產品類型。
3. E1 使用原始繁中／英文候選與 review-time semantic normalization，沒有做逐句同語言翻譯；語言／格式仍是殘餘 confound。
4. E2 是由 Main 對完整 final plan 做 editorial compression，沒有保存同一份原始 issue ledger 供兩個 synthesis 重跑。
5. E3 三個 arms 由同一 Main 整合，雖固定專業 skeleton、格式與字數，仍可能包含 synthesis judgment confound；尤其 Split arm 的 over-constraint 是「role findings＋Main 編譯方式」共同結果，不能歸咎角色本身。
6. 沒有量測 token、延遲或金錢；席位與 perspective turns 不能直接換算成本。
7. Judges 使用相同 host default model family，但 context、role lens 與候選位置獨立；這不是跨模型一致性測試。

## 對 meeting core 與 GUI 的建議

### Runtime／skill 邏輯

1. 保留目前兩層：Main → roles；department 只是 affiliation label，不新增 leader／department weight。
2. Main 提議 complexity range、總席位與同專業席位數；使用者可調整。
3. actual-user seat selection 另看 actor 的 permission、evidence、irreversible action 與 failure consequence，不與 professional complexity 綁死。
4. actual-user opening 的輸出型別應是 `goal／information_need／misunderstanding／unacceptable_failure／minimum_success`；critique 應是 `accept／revise／question＋consequence＋smallest correction`。
5. Main synthesis 增加明確的 **authority back-propagation gate**：user correction 若改變 state、API、physical control 或 policy，先送專業 owner 驗證，不能直接升格成 invariant。
6. 增加 **proportionality pass**：把不可證明的 absolute requirement 改成 evidence-bound control、exception path 或待權威決策。
7. 輸出採主 plan＋technical appendix，避免角色減少後仍輸出過長，也避免 35–38% uniform compression 刪掉 recovery contract。

### GUI 可視化

GUI 應讓使用者看見並調整：

- Main 建議的 complexity 與每個 role 的邀請原因；
- professional／actual-user type、department label、owned／excluded surfaces；
- actual-user 是 simulated lens 而非研究的警告；
- Phase 1 task model、Phase 2 claim dispositions；
- finding 進入 final plan 前經過的 authority owner、accepted／rejected／bounded 狀態；
- 角色數增加帶來的 coverage delta，而不是票數或 department weight；
- 主文件與附錄的壓縮層級切換。

## Completion receipt

- `evalrev-large-vs-compact-r1`：3/3 roles completed，無 retry、無 degradation；chat-only PlanRevision，digest 未 materialize。
- `evalrev-synthesis-compression-r1`：3/3 roles completed，無 retry、無 degradation；chat-only PlanRevision，digest 未 materialize。
- `planrev-address-user-ablation-r1`：5/5 content roles completed，其中 4 個 actual-user roles 各完成兩階段；3/3 evaluator roles completed；無 retry、無 degradation；chat-only PlanRevision，digest 未 materialize。
- Missing planned roles：none。
- 評估 gate：**PASS**；E3 候選實作 readiness：**PASS_WITH_CHANGES**，需先閉合 `EXP3-LABEL-DEADLOCK`。
