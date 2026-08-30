# Meeting core 3–4 人 compact panel 規劃品質評估

- 評估日期：2026-08-29
- 評估範圍：GUI 實作前的 plan／spec 品質，不是 implementation 品質
- 狀態：三案 compact meeting 與 fresh blind review 已完成
- 前次實驗：[Meeting core 規劃品質對照評估](meeting-core-quality-comparison.zh-TW.md)

> 2026-08-30 後續控制實驗已完成：Compact 對 Large 的同批直接盲評為 9–0；35–38% synthesis compression 仍維持高品質但略輸完整版；actual-user ablation 顯示拆席能提高 finding recall，卻需要 Main 做 authority back-propagation 與 proportionality adjudication。詳見 [Meeting core 後續控制實驗](meeting-core-follow-up-experiments.zh-TW.md)。

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

## Confirmed role definitions 與執行紀錄

以下補齊本輪 11 個角色的 frozen role cards，讓後續能追查「哪個責任被合併」、「哪個使用者視角提出修正」與「是否需要重新拆出 specialist」。

### 任務 1／2／3 角色速查

| 任務 | Plan revision | 人數 | 本案實際使用角色 |
| --- | --- | ---: | --- |
| **任務 1：候補名單自動遞補** | `planrev-compact-waitlist-r1` | 4 | `W1` Waitlist Capacity and Service Design Generalist（專業）；`W2` Public Waitlist Customer（終端使用者）；`W3` Frontline Calendar Operator（終端使用者）；`W4` CMS Waitlist Operations Operator（終端使用者） |
| **任務 2：出貨前修改地址** | `planrev-compact-address-r1` | 4 | `A1` Order Address Change and Fulfillment Design Generalist（專業）；`A2` Purchasing Customer（終端使用者）；`A3` Warehouse/Fulfillment Operator（終端使用者）；`A4` CMS Support/Operations Operator（終端使用者） |
| **任務 3：CRM CSV 聯絡人匯入** | `planrev-compact-csv-r1` | 3 | `C1` CRM Import Product and Application Generalist（專業）；`C2` Contact Data Correctness and Recovery Reviewer（專業）；`C3` Workspace Admin Import Operator（終端使用者） |

因此三案不是共用一組角色：任務 1 使用 `W1–W4`，任務 2 使用 `A1–A4`，任務 3 使用 `C1–C3`。下方詳細卡片沿用相同編號。

共同條件：

- 三份 slate 都由 Main 完整產生後交由使用者 review；使用者沒有修改角色，也沒有匯入外部 ChatGPT／Claude prompt。
- 所有角色 provenance 均為 `main_generated`，沒有 parent role revision；Main 是召集人與綜合者，不是席位。
- `department` 只是專業歸屬標籤，不是第三層組織、leader、票數或權重。每個角色直接向 Main 提交自己的公開 findings。
- 所有角色都使用 fresh internal context、read-only、不可查看其他角色原始輸出、baseline、rubric 或預期答案，也不可自行擴張 scope／authority。
- 三案採 chat-only conversation snapshot freeze，沒有建立 durable meeting-plan bundle，因此 plan／role digests 當時沒有 materialize。報告不事後虛構 digest；下列穩定 identity 以實際執行使用的 `role_id`／`role_revision_id` 為準。
- 下列 `coverage` 代碼是為後續分析新增的 report-local locator，不宣稱是原 frozen plan 的 machine `risk_surface_id`。

### 任務 1：候補名單自動遞補

- Plan revision：`planrev-compact-waitlist-r1`
- Mode：`design`
- Complexity range：`standard`
- Frozen seats：4
- 執行結果：4 個角色完成；3 個 simulated actual-user roles 另完成 bounded UI critique
- 已揭露並由確認動作接受的 coverage warning：只有一個專業席，沒有獨立專業角色挑戰容量、通知或 policy 設計；Main 必須在 synthesis 加強 concurrency 與 policy validation。

#### W1. Waitlist Capacity and Service Design Generalist

- `role_id`：`role-compact-waitlist-generalist`
- `role_revision_id`：`rolerev-compact-waitlist-generalist-r1`
- Department／type：Product & Domain Engineering／professional
- Lens question：如何在不建立第二套容量 authority 的前提下，把候補需求、邀請權利、通知投遞與既有 booking／calendar 流程整合成可閉合、可恢復的服務 contract？
- Selection reason：本輪刻意把一般 product、domain architecture、reliability、notification recovery 與 compatibility 責任合併，檢查一個 generalist 是否足以處理中型共享狀態問題。
- Coverage：`W-CAPACITY-AUTHORITY`、`W-LIFECYCLE`、`W-NOTIFICATION-RECOVERY`、`W-CONCURRENCY`、`W-CONTRACTS`、`W-COMPAT-ROLLOUT`
- Responsibilities：定義唯一容量 authority、entry／offer／notification-attempt lifecycle、接受邀請的 transaction／idempotency、manual booking/block races、時區、data/API/events、permissions/audit、reconciliation、相容、rollout、tests、observability 與實作順序；發布 `W-UI-CUST-*`、`W-UI-FRONT-*`、`W-UI-CMS-*` bounded claims。
- Explicitly excluded：不得決定 FIFO、邀請期限、requeue、staff override、永久通知失敗、suitability 或是否 reserve capacity 等未授權產品政策；不得用通知 callback 當容量 truth；不得宣稱真實使用者研究或直接實作。
- Required evidence／deliverables：task invariants、state／race table、明確 decision list、三介面 UI claims、API/event/timezone/permission contract、failure recovery、compatibility 與候選 plan outline。
- Authority limits：既有 booking/calendar capacity contract 控制容量；產品 owner 控制 fairness／promise／override policy；既有 permissions 與 compatibility contract 控制存取及舊流程。
- Execution：一個 independent professional opening；`completed`。
- Material contribution：建立「booking/calendar 是唯一 capacity authority；waitlist demand、offer right、notification delivery 分離」的主模型，並列出 acceptance/expiry/manual action interleavings、reconciliation 與 activation 前的 policy gates。

#### W2. Public Waitlist Customer

- `role_id`：`role-compact-waitlist-customer`
- `role_revision_id`：`rolerev-compact-waitlist-customer-r1`
- Department／type：Simulated Actual-User Lens／public customer
- Lens question：候補客戶如何確認自己只是 waiting、必須採取行動、已正式 booked，或已 expired／withdrawn，並在通知延遲與接受結果不明時安全恢復？
- Selection reason：客戶承受 false confirmation、過期連結、錯誤時區與未知接受結果，這些後果不能由 technical correctness 代替。
- Coverage：`W-CUSTOMER-JOURNEY`、`W-CUSTOMER-STATUS`、`W-CUSTOMER-RECOVERY`
- Responsibilities：Phase 1 在未看 UI 提案前建立 goals、information needs、misunderstandings、unacceptable failures 與 minimum success；Phase 2 只檢查 `W-UI-CUST-*` claims 的狀態文字、時區、booking confirmation、retry 與下一步。
- Explicitly excluded：不設計 architecture、不選 fairness／requeue policy、不主張實際偏好、普遍性、可用性或 compliance。
- Required evidence／deliverables：unanchored customer task model；對 bounded claims 逐項 `accept／revise／question`；保留 residual research questions。
- Authority limits：simulation 只能揭露可能的理解與恢復風險；正式政策與真實 usability 必須由產品 authority 與使用者研究決定。
- Execution：opening + bounded critique；兩階段皆 `completed`。
- Material contribution：要求 customer-visible states 不可只寫模糊的 `closure`；邀請必須顯示精確日期、時間與具名分店時區；只有 authoritative booking confirmation 才能顯示 booked；任何失敗都要說明仍在 waiting、已 requeue 或應聯絡哪個分店。

#### W3. Frontline Calendar Operator

- `role_id`：`role-compact-waitlist-frontline`
- `role_revision_id`：`rolerev-compact-waitlist-frontline-r1`
- Department／type：Simulated Actual-User Lens／frontline operations
- Lens question：第一線人員在 offer、手動 booking、block、expiry 與通知狀態重疊時，如何快速辨認真正容量狀態並安全完成或停止操作？
- Selection reason：第一線會直接製造 physical/operational conflict，也必須對客戶說明結果；其操作資訊需求不同於 customer 與 CMS policy management。
- Coverage：`W-FRONTLINE-CAPACITY-VIEW`、`W-MANUAL-ACTION-CONFLICT`、`W-FRONTLINE-ESCALATION`
- Responsibilities：Phase 1 建立 authoritative capacity picture、stale-state、manual action、customer wording、branch timezone 與 escalation task model；Phase 2 critique `W-UI-FRONT-*` calendar claims。
- Explicitly excluded：不決定 override policy、不重設 booking domain、不以通知 log 推斷容量、不主張真實操作頻率或 usability。
- Required evidence／deliverables：操作所需資訊、likely misoperation、conflict outcomes、safe customer wording、stop-and-escalate path，以及 bounded claim dispositions。
- Authority limits：existing calendar/booking authority 與 branch permissions 控制；simulation 不能授權 override。
- Execution：opening + bounded critique；兩階段皆 `completed`。
- Material contribution：要求 offer hold 必須與 booking/block 明確區分、顯示 branch-local timezone 與 version freshness；衝突不能只保證 transaction 正確，UI 還必須呈現無 mutation／authorized revocation 的結果、客戶影響與 escalation。

#### W4. CMS Waitlist Operations Operator

- `role_id`：`role-compact-waitlist-cms`
- `role_revision_id`：`rolerev-compact-waitlist-cms-r1`
- Department／type：Simulated Actual-User Lens／legacy CMS operations
- Lens question：CMS 營運如何配置、啟用、監看與恢復跨分店候補流程，而不靠 hidden defaults、廣泛 override 或刪除歷史？
- Selection reason：CMS 操作者負責 policy visibility、exceptions、audit 與 recovery，其風險不同於第一線即時行事曆操作。
- Coverage：`W-CMS-POLICY`、`W-CMS-PERMISSIONS`、`W-CMS-RECOVERY`、`W-CMS-AUDIT`
- Responsibilities：Phase 1 建立 effective policy、configuration precedence、permissions、exceptions、recovery、audit 與 rollout task model；Phase 2 critique `W-UI-CMS-*` activation/recovery claims。
- Explicitly excluded：不自行決定 fairness、delivery failure、override 或 capacity policy；不宣稱 compliance 或實際 operator preference。
- Required evidence／deliverables：required-policy inventory、likely misconfiguration、minimum success、exception/recovery needs、bounded claim dispositions。
- Authority limits：existing CMS RBAC 與 authoritative business rules 控制；simulation 只揭露 operator consequences。
- Execution：opening + bounded critique；兩階段皆 `completed`。
- Material contribution：要求 activation review 顯示每個 effective policy 的 value、source、scope、precedence 與 version；recovery controls 必須 least-privilege、reason-coded、previewable、idempotent，且逐筆呈現 success/skip/conflict/failure。

### 任務 2：出貨前修改地址

- Plan revision：`planrev-compact-address-r1`
- Mode：`design`
- Complexity range：`standard`
- Frozen seats：4
- 執行結果：4 個角色完成；3 個 simulated actual-user roles 另完成 bounded UI critique
- 已揭露並由確認動作接受的 coverage warning：沒有獨立 carrier、data 或 commercial-policy specialist；不確定 authority 必須保留為 bounded decisions，不可由 generalist 擅自增加預設政策或沒有 exit 的狀態。

#### A1. Order Address Change and Fulfillment Design Generalist

- `role_id`：`role-compact-address-generalist`
- `role_revision_id`：`rolerev-compact-address-generalist-r1`
- Department／type：Product & Fulfillment Engineering／professional
- Lens question：如何用一個 authoritative address version 與可閉合的 fulfillment coordination contract，安全處理 customer／CMS change、warehouse progression 與 carrier label races？
- Selection reason：本輪合併 product/domain、fulfillment architecture、carrier recovery、compatibility 與基本 policy-boundary 責任，避免 specialist 各自新增互不相容的 states。
- Coverage：`A-ADDRESS-AUTHORITY`、`A-REQUEST-LIFECYCLE`、`A-FULFILLMENT-RACE`、`A-LABEL-RECOVERY`、`A-POLICY-BOUNDARY`、`A-COMPAT-ROLLOUT`
- Responsibilities：定義 immutable revisions、唯一 order pointer、request lifecycle、CAS/idempotency、shared ship guards、必要且有 exit 的 fulfillment gate、label generations、late/out-of-order callbacks、tax/shipping/zone/fraud bounded decisions、三介面 claims、audit、compatibility、rollout/tests/observability 與實作順序。
- Explicitly excluded：不得把 carrier callback 當 address authority；不得在 authority 缺席時決定費用、稅務、zone、fraud、state cutoff 或 generic override；不得新增無 closure 的 states；不得直接實作。
- Required evidence／deliverables：actor/state decision matrix、single-pointer invariant、request/gate/label lifecycle、race/recovery table、policy decision table、`A-UI-*` claims 與候選 plan outline。
- Authority limits：existing order/fulfillment state machine、warehouse operations、carrier contract、tax/shipping/fraud policy 與 compatibility contract 控制各自 domain。
- Execution：一個 independent professional opening；`completed`。
- Material contribution：把前次混雜的 `applied` 拆回唯一 address pointer、獨立 request、必要 gate 與 generation-scoped label；carrier result 只能更新自己的 generation；所有 policy gaps 都列為 blocking decisions。

#### A2. Purchasing Customer

- `role_id`：`role-compact-address-customer`
- `role_revision_id`：`rolerev-compact-address-customer-r1`
- Department／type：Simulated Actual-User Lens／purchasing customer
- Lens question：客戶如何知道現在是否仍可改、哪個地址真正控制出貨，以及費用／稅／zone／fraud consequence 是否仍待處理？
- Selection reason：客戶最主要的風險是把「request received」誤認為「address changed」，並在 race loss 後不知道貨會寄去哪裡。
- Coverage：`A-CUSTOMER-ELIGIBILITY`、`A-CUSTOMER-AUTHORITATIVE-RESULT`、`A-CUSTOMER-CONSEQUENCE-RECOVERY`
- Responsibilities：Phase 1 建立 eligibility、information、consent、retry、race-loss 與 support task model；Phase 2 critique `A-UI-CUST-*` claims。
- Explicitly excluded：不決定 pricing/tax/fraud/fulfillment policy，不主張實際 preference、usability、prevalence 或 compliance。
- Required evidence／deliverables：unanchored customer journey、unacceptable failures、minimum success，以及每個 bounded claim 的 disposition／revision。
- Authority limits：existing commercial、tax、fraud、fulfillment 與 carrier rules 控制；simulation 不能把未知 consequence 當成 no change。
- Execution：opening + bounded critique；兩階段皆 `completed`。
- Material contribution：要求 action availability 必須標示仍會在 submit 時重驗；current address 與 proposed address 分開；只有 `APPLIED` 才改權威顯示；每種 cutoff、review、denial、race-loss 或 failure 都要顯示是否套用、當前地址與 safe next action。

#### A3. Warehouse/Fulfillment Operator

- `role_id`：`role-compact-address-warehouse`
- `role_revision_id`：`rolerev-compact-address-warehouse-r1`
- Department／type：Simulated Actual-User Lens／warehouse operations
- Lens question：倉儲在 allocation、picking、label、packing 與 handoff 過程中，如何避免 stale screen／printed artifact 把舊地址帶進實體出貨？
- Selection reason：physical/digital divergence 的後果與證據只會在 warehouse workflow 出現，不能由 customer 或 backend lens 代替。
- Coverage：`A-WAREHOUSE-STATE`、`A-PHYSICAL-ARTIFACT`、`A-RECONCILIATION`、`A-SHIP-GUARD`
- Responsibilities：Phase 1 建立每個 checkpoint 的資訊、misoperation、unacceptable divergence、pause/escalation 與 recovery task model；Phase 2 critique `A-UI-WH-*` claims。
- Explicitly excluded：不得選 authoritative address、決定 commercial/fraud policy、聲稱 carrier/warehouse policy 或實際 usability。
- Required evidence／deliverables：operator-visible state、irreversible checkpoints、artifact-version mismatch、reconciliation actions、bounded claim dispositions。
- Authority limits：existing fulfillment authority 與 carrier/warehouse procedures 控制；warehouse acknowledgement 不等於 address approval。
- Execution：opening + bounded critique；兩階段皆 `completed`。
- Material contribution：要求所有 fulfillment/scanning surfaces 顯示 gate、authority revision、request metadata、label generation 與唯一下一步；stale scan 必須拒絕但優先導向可恢復動作；warehouse acknowledgement 只能證明 reconciliation，不能切換 address pointer。

#### A4. CMS Support/Operations Operator

- `role_id`：`role-compact-address-cms`
- `role_revision_id`：`rolerev-compact-address-cms-r1`
- Department／type：Simulated Actual-User Lens／CMS support and operations
- Lens question：客服如何 inspect、代客提出、說明與恢復 address change，而不變成 warehouse、carrier、tax 或 fraud 的第二 authority？
- Selection reason：CMS 需要比客戶更完整的 evidence 與 recovery controls，但 unrestricted edit／override 會繞過所有 invariants。
- Coverage：`A-CMS-INSPECTION`、`A-CMS-GUARDED-ACTIONS`、`A-CMS-AUDIT`、`A-CMS-ESCALATION`
- Responsibilities：Phase 1 建立 support information、guided flow、permissions、audit、failure ownership 與 recovery queues；Phase 2 critique `A-UI-CMS-*` claims。
- Explicitly excluded：不決定 override、tax、shipping、fraud、warehouse 或 carrier policy；不主張實際 usability／prevalence／compliance。
- Required evidence／deliverables：operator task model、misoperation、minimum success、authority questions、bounded claim dispositions。
- Authority limits：existing CMS RBAC 與各 domain owner 控制；actor identity 必須來自 authenticated session，不能由 operator 自填。
- Execution：opening + bounded critique；兩階段皆 `completed`。
- Material contribution：要求 CMS 顯示 authoritative/proposed field diff、failure/retry、decision owner、queue/escalation 與 audit；unavailable actions 應顯示 blocking reason；revert 必須建立新 proposal；generic override 在 scope、states、approver/executor 與 evidence 未決前不得出現。

### 任務 3：CRM CSV 聯絡人匯入

- Plan revision：`planrev-compact-csv-r1`
- Mode：`design`
- Complexity range：`lightweight`
- Frozen seats：3
- 執行結果：3 個角色完成；Workspace Admin 另完成 bounded UI critique
- Coverage warning：沒有發現 critical coverage gap。Data correctness/recovery 被保留為獨立專業席，因為 identity corruption 與 reference-safe rollback 的 evidence／failure consequence 不適合完全合併進一般 application role。

#### C1. CRM Import Product and Application Generalist

- `role_id`：`role-compact-csv-generalist`
- `role_revision_id`：`rolerev-compact-csv-generalist-r1`
- Department／type：Product Engineering／professional
- Lens question：如何在沒有 background jobs 的小型 CRM 中，重用既有 CRUD truth，提供完整而比例適當的 upload／mapping／preview／commit／results 流程？
- Selection reason：一般 product、application architecture、permissions、synchronous limits、UI contract、compatibility 與 rollout 可以由一個 generalist 閉合。
- Coverage：`C-ADMIN-WORKFLOW`、`C-CRUD-AUTHORITY`、`C-PERMISSIONS`、`C-SYNC-LIMITS`、`C-API-UI`、`C-COMPAT-ROLLOUT`
- Responsibilities：定義 staged Admin workflow、既有 CRUD validation authority、mapping/mode、permissions、foreground limits、data/API、audit、compatibility、tests/observability、implementation order，並發布 `C-UI-ADMIN-*` claims。
- Explicitly excluded：不得發明 destructive rollback、identity matching 或背景工作系統；不得加入無關 security/platform architecture；不得直接實作。
- Required evidence／deliverables：runtime authority gaps、workflow and API contract、bounded product decisions、UI claims、performance gates 與候選 plan outline。
- Authority limits：existing CRUD validation/normalization、workspace permission、external references 與 audit/retention 控制；未提供的 runtime 行為是 release gate。
- Execution：一個 independent professional opening；`completed`。
- Material contribution：主張 import 是 CRUD orchestration 而非第二套 validation；建立 all-row preview、row-atomic partial result、durable retry identity、10k boundary、Admin-only contract 與 explicit blank/tag semantics。

#### C2. Contact Data Correctness and Recovery Reviewer

- `role_id`：`role-compact-csv-data-recovery`
- `role_revision_id`：`rolerev-compact-csv-data-recovery-r1`
- Department／type：Data Quality & Recovery／professional
- Lens question：什麼 matching、row disposition、idempotency 與 compensation contract 才能避免更新錯人、重播成功列或在 rollback 時破壞後續編輯與 references？
- Selection reason：wrong-contact update 與 destructive recovery 是 CSV 匯入最難修復的後果，需要與一般產品流程分開檢查。
- Coverage：`C-MATCH-DEDUP`、`C-ROW-STATE`、`C-PARTIAL-FAILURE`、`C-IDEMPOTENT-RETRY`、`C-REFERENCE-SAFE-ROLLBACK`
- Responsibilities：定義 conservative identity options、within-file duplicates、preview/write-time validation、row/import state、systemic failure、retry boundary、immutable manifest、before/after evidence、dry-run compensation 與 2k/10k test risks。
- Explicitly excluded：不得自行決定 business identity policy、推薦 background jobs、設計完整 UI 或一般平台架構、執行資料變更。
- Required evidence／deliverables：match decision options、row/import disposition model、failure/retry/rollback contracts、test risks 與 authority gaps。
- Authority limits：existing CRUD normalization/uniqueness/deletion/reference rules 控制；缺少 evidence 時 ambiguity 必須 block，不能 fallback 猜測。
- Execution：一個 independent professional opening；`completed`。
- Material contribution：拒絕 name/company/tags 自動識別與未證明的 phone fallback；要求 row result 與 manifest identity 不可變；retry 只處理 unfinished/transient rows；rollback 必須 version-checked、reference-safe、idempotent，且允許正確地完成為 partial。

#### C3. Workspace Admin Import Operator

- `role_id`：`role-compact-csv-admin`
- `role_revision_id`：`rolerev-compact-csv-admin-r1`
- Department／type：Simulated Actual-User Lens／workspace administration
- Lens question：Admin 如何在大批資料中確認 mapping 與 identity 行為、理解每列結果、安全重試並在出錯時恢復，而不承受 hidden clearing／merge／duplicate submit？
- Selection reason：這案只有一個主要操作者，但其 preview、confirmation、result reconciliation 與 rollback information needs 仍不能由 application role 自行驗證。
- Coverage：`C-ADMIN-MAPPING-SAFETY`、`C-ADMIN-PREVIEW`、`C-ADMIN-RESULTS`、`C-ADMIN-RETRY-ROLLBACK`
- Responsibilities：Phase 1 建立 upload/detect/map/preview/confirm/results、likely misoperation、minimum success、audit/recovery task model；Phase 2 critique `C-UI-ADMIN-*` claims。
- Explicitly excluded：不決定 identity、retention、delete/reference 或 compliance policy；不宣稱實際 preference、usability 或 prevalence。
- Required evidence／deliverables：unanchored operator workflow、mapping hazards、unacceptable failure、bounded claim dispositions 與 residual policy questions。
- Authority limits：existing CRM CRUD 與 workspace rules 控制；simulation 不能用操作方便覆蓋資料正確性。
- Execution：opening + bounded critique；兩階段皆 `completed`。
- Material contribution：要求 preview counts 互斥且與所有 source rows 對帳；result manifest 不可變並保留 field-level errors；retry 必須定義 exact identity、retention 與 fresh validation；因任務明確要求 rollback，v1 必須提供 conflict-aware dry-run/compensation，或由產品明確移除 scope。

### Cross-role coverage map

| 任務 | 合併的專業 ownership | 獨立 challenge | 仍刻意保留的缺口／gate |
| --- | --- | --- | --- |
| 候補名單 | 容量、state、notification recovery、API/events、compatibility 全由 W1 負責 | W2 客戶、W3 第一線、W4 CMS 從實際操作後果挑戰 UI／policy | 沒有第二個 technical lens；容量 promise 與 fairness policy 必須在 implementation 前決定 |
| 地址變更 | address authority、request/gate/label、carrier recovery、policy boundary、compatibility 全由 A1 負責 | A2 客戶、A3 倉儲、A4 CMS 分別挑戰 digital promise、physical artifact 與 support authority | 沒有 carrier／tax／fraud specialist；runtime 或 authority 不支持的 branch 不得啟用 |
| CSV 匯入 | workflow、CRUD reuse、permissions、foreground scale、UI/API 由 C1 負責 | C2 專門挑戰 identity/retry/rollback；C3 挑戰 Admin operability | email uniqueness、delete/reference 與 retention 必須先取得 runtime evidence |

這張 map 也是後續增減角色的基準：若要再拆席，應指出上表哪一項 evidence 或 authority 目前無法由 owner 安全處理；不能只因出現「security」、「architecture」或「reliability」關鍵字就新增角色。

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
