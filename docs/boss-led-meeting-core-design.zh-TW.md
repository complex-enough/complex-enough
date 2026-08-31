# 老闆召集式多視角會議核心設計

- 決策日期：2026-08-26
- 實作更新：2026-08-29
- 產品／證據更新：2026-08-31
- 文件狀態：`implementation_validated_behavioral_release_pending`
- runtime 狀態：portable instructions、contracts、validators 與 deterministic tests 已實作；2026-08-29 range-calibrated runtime 尚待 fresh behavioral release scorecard
- 依據：使用者確認的產品主軸、現行 repo 契約與四個 fresh-context 設計視角
- 下一階段：凍結 plan-only core protocol、完成 N-task 效果驗證與 current-runtime Codex behavioral release scorecard 後進入 GUI 產品與實作階段；Claude Code 仍需獨立 behavioral scorecard

## 文件邊界

這份文件定義 skill 的目標行為，並作為 meeting-core 的產品／架構基線。2026-08-28 的上一版 runtime 已完成 Codex release validation；2026-08-29 加入角色拆分 range 後，deterministic validation 已更新，fresh behavioral release validation 尚待完成。GUI 尚未實作。

先前對話曾人工模擬「main 先產生角色卡、使用者確認後才開會」的流程，用途是 dogfood 互動模型。該次模擬本身仍不是實作證據；後續 runtime instructions、meeting-plan v1.1、panel-output v1.2、semantic/bundle validators 與 deterministic tests 才是目前的 implementation evidence。

目前 runtime 以 [`SKILL.md`](../SKILL.md)、[`references/`](../references/)、[`schemas/meeting-plan.schema.json`](../schemas/meeting-plan.schema.json)、[`schemas/panel-output.schema.json`](../schemas/panel-output.schema.json) 與 validators/tests 為準。Codex v1.1 [2026-08-28 scorecard](../evals/results/codex-2026-08-28.json) 已通過 21/21 cases、49 個公開回合與 95/95 fresh blind assertions，但只綁定 range 變更前的 runtime；目前作為歷史證據，不再滿足 current-runtime release gate。

2026-08-31 的 [使用者驗證 Plan Pilot](evaluations/meeting-core-user-validated-plan-pilot.zh-TW.md) 是 clarified core claim 的第一份直接證據：`Main＋領域專業＋模擬 End user` 的 plan-only Treatment 在三位 fresh 模擬租戶盲評中以 3–0 勝過一般 Agent，平均差 `+0.604/5`。這是單案方向性訊號，還不能取代 N-task 驗證。先前的[規劃品質比較](evaluations/meeting-core-quality-comparison.zh-TW.md)、[Compact panel 實驗](evaluations/meeting-core-compact-panel-comparison.zh-TW.md)及[後續控制實驗](evaluations/meeting-core-follow-up-experiments.zh-TW.md)保留為技術型 meeting 的次要機制證據。

### 目前實作狀態

| Surface | 狀態 |
| --- | --- |
| main-generated-first role slate 與每輪 review/freeze runtime | 已寫入 portable skill instructions |
| 角色 edit/add/remove/merge/split/reset/import 語意 | 已寫入 runtime reference 與 meeting-plan contract |
| 外部 prompt normalization／conflict governance | 已寫入 runtime reference 與 schema/validator invariants |
| meeting-plan v1.1（相容 v1.0）、panel-output v1.2、bundle validation | 已實作並有 positive/negative deterministic tests |
| 角色拆分複雜度 | `lightweight`／`standard`／`critical` 已寫入 runtime 與 meeting-plan v1.1 |
| 實際使用者視角 | 與專業複雜度分離；支援 unanchored opening 與 UI claim critique |
| v1.0/v1.1 panel-output compatibility | deterministic fixtures/tests 通過 |
| neutral multi-turn eval definitions | current suite 24 cases；上一 runtime 的 21-case suite 已完成 fresh isolated execution，共 49 個公開回合 |
| Codex meeting-core behavioral status | range 變更前為 `GO`；current runtime fresh release run pending |
| release scorecard gate | 歷史結果只做封存完整性驗證；current GO 必須重新綁定 current suite/runtime/artifacts |
| Claude Code behavioral status | structural only |
| GUI | current-runtime behavioral gate pending；GUI 尚未實作 |

## 核心產品定義

Skill 的主體是一位代表使用者召集會議的老闆／main，而不是固定專家 roster，也不是要求使用者自行組 panel。

### 產品目標與 Plan → Spec 交接邊界

對產品、流程與 UIUX 類任務，skill 的首要目標是改善最上游的 Plan：讓需求先經過領域專業與實際承受流程後果的 End-user lens，降低單一 Agent 過度思考、補入不必要功能，或產生不符合現場 task model 的設計。它不以取代後續普通 Agent 的技術設計與實作流程為目標。

```text
階段 1：Main＋領域專業＋End user
  → 釐清真實任務、資訊時機、UIUX、誤操作後果與最低成功

階段 2：Main 產生使用者檢查過的 Plan
  → task flow、畫面骨架、可見狀態、操作、恢復與待決政策

階段 3：普通 Agent 沿既有流程接手
  → 依 Plan 產生技術 Spec、implementation plan、實作與測試
```

技術角色不是階段 1 的預設席位。只有當已知技術限制會實質改變產品選項、可行性或高後果安全邊界時，Main 才應建議在該輪加入相應專業；一般前後端、架構、資安與資料設計由後續 Agent 依正常工程流程處理。這不代表技術「一定做得到」，而是避免在使用者任務尚未穩定前，讓 implementation concern 主導或膨脹產品 Plan。

用於驗證核心效果的比較實驗應停在 Plan：Control 是一般 Agent 直接規劃；Treatment 是先完成上述使用者驗證流程。兩者由 fresh 模擬 End users 盲評任務符合、資訊時機、狀態清晰、誤操作、恢復、比例原則與 Spec handoff，不把技術欄位完整度列入本階段分數。

```text
使用者提出會議議題
  → main 理解目標、權威、scope 與風險面
  → main 自行決定要找幾個部門、哪些部門
  → main 完整產生每個部門的角色定義
  → 使用者檢查已完成的角色提案
  → 使用者可直接接受、調整，或匯入外部產生的角色定位 prompt
  → main 重新檢查重疊與風險 coverage
  → 使用者確認，原子化凍結本輪 role slate
  → skill 在 fresh internal contexts 執行各角色
  → 獨立 opening 完成後才進入主持討論
  → main 驗證證據、裁決並關閉本輪
  → 下一輪重新判斷需要哪些部門
```

### 不可改變的主軸

- main 是會議召集人、主持人與最終 accountable owner，不算一個 perspective seat。
- 每輪的完整預設角色一定由 main 先產生；使用者不需要從空白畫面 staffing the meeting。
- 使用者可以接受、修改、新增、移除、合併、拆分或匯入角色 prompt。
- 外部 ChatGPT／Claude 只可能是角色定位 prompt 的作者來源，不是 meeting executor，也不需要等待外部模型回覆。
- 最終角色仍由 skill 內部 fresh-context subagent 執行；capacity 不足使用 waves，不刪除已確認角色。
- 角色自訂不得擴張 authority、scope、工具權限、外部寫入、independence 或 response contract。
- 會議不以投票決定真實性；main 依 authority 與 reproducible evidence 裁決。
- 每輪重新評估部門組成，不把上一輪 slate 當成固定組織。

## 參與者與責任

### Human user

- 提供會議目標、產品方向與真正需要 human decision 的事項。
- 檢查 main 已產生的完整角色 slate 是否偏離意圖。
- 可接受全部角色，或對特定角色執行語意化修改。
- 對移除 critical coverage、產品方向、scope、外部承諾或重大成本作真正決策。
- 不負責 model routing、waves、retry、一般 wording normalization 或 moderator 技術判斷。

### Main／boss／convener

- 建立 authority packet、risk-surface map 與最小充分角色 slate。
- 完整產生所有預設角色與選用理由。
- 正規化使用者修改或匯入的角色 prompt，顯示差異與衝突。
- 每次 draft 變更後重算 overlap、critical coverage 與 marginal value。
- 凍結後依確定版本 dispatch，不允許 prompt drift。
- 建立 public issue register、主持 challenge/rebuttal、親自驗證重大證據。
- 最終接受、駁回、延後、標示 out-of-scope 或提出真正 user gate。
- 不以自己的立場增加一張 perspective vote。

### Logical professional perspective role

- 是一條穩定的專業視角 lineage，以 `role_id` 識別。
- 每次修改產生新的 immutable `role_revision_id`。
- 負責一組明確 risk surfaces、lens question、evidence duties 與 public deliverable。
- 不是一次 agent execution；一次或多次執行嘗試以 `perspective_id` 另行記錄。
- `department` 只是專業歸屬標籤，不是獨立 entity、父層 roster 或權重層。
- main 可依風險與資訊價值，為同一 department 產生多個不同 lens 的角色；每個角色都要能獨立說明問題、證據責任與風險 ownership。
- 同部門多席表示需要更深的覆蓋，不增加票數或決策權；不得用複製角色製造共識。

### Internal perspective attempt

- 由 frozen `role_revision_id` 編譯後在 fresh context 執行。
- 收到相同 authority snapshot、自己的 EffectiveRole、可讀 artifacts 與 response contract。
- 不收到 raw imported prompt、peer raw reports、moderator 偏好或 evaluator criteria。
- retry/replacement 必須沿用同一 frozen role revision；改角色不是 retry，而是新 round。

### External prompt author

- 只是使用者宣稱的角色 prompt 來源，例如 ChatGPT、Claude 或其他工具。
- Provider/author label 屬於 user-declared provenance，skill 不宣稱已驗證真實身份。
- 不獲得 executor、tool、authority 或 meeting-participant 身份。

## Meeting 與 round 模型

### Meeting

Meeting 代表完整目標，可包含一個或多個 ordered rounds。

- `meeting_id`
- objective、scope、non-goals、authority references
- current round
- public status 與 terminal condition
- ordered round references

### MeetingRound

每個 round 只負責一個 mode 或 `full_cycle` stage，並擁有一份獨立、可確認的 role slate。

- `round_id`
- sequence、mode/stage、agenda
- `supersedes_round_id` 或 prior-round handoff
- active `plan_revision_id`
- frozen plan reference
- run/result reference

### 建議狀態機

```text
generating_roles
  → awaiting_role_review
  → frozen
  → queued
  → independent_opening
  → deliberating
  → verifying
  → adjudicating
  → completed
```

補充狀態：

- `needs_attention`：有可恢復問題，但需要明確 recovery action 或缺少外部輸入。
- `cancel_requested`：取消已提出，等待安全 terminal point。
- `cancelled`：本輪已取消並留下公開原因。
- `failed`：不可恢復的執行失敗；failure phase 與 coverage effect 必須公開。

`completed` 代表記錄已完整關閉，不代表結果一定成功；close gate 仍可能是 `continue`、`revise`、`go`、`no_go` 或 `blocked`。

### 角色確認與 freeze

- `awaiting_role_review` 只在 main 已產生完整預設 slate 後出現。
- 所有 edit/add/remove/merge/split/import 都以 copy-on-write 產生新 PlanRevision。
- 每次修改後顯示 role diff、coverage delta、overlap/drift warning 與 lineage。
- `confirm_and_start(expected_plan_revision_id, expected_digest)` 必須原子化完成確認與 freeze，避免確認後又被 stale edit 改動。
- `confirm_and_start` 是 review/freeze checkpoint，不等於 `needs_user_decision`。
- Freeze 後不可原地修改角色；若需換部門或改角色，必須建立新 round 或 superseding round。
- 一鍵 `使用 main 產生的角色並開始` 必須是主要路徑；細部編輯採 progressive disclosure。

## RoleDefinition

### 完整角色卡

main 產生的每個角色至少包含：

- `role_id`
- `role_revision_id`
- department/name
- `lens_question`
- `selection_reason`
- owned `risk_surface_ids` 與 criticality
- responsibilities
- explicit exclusions
- required evidence
- expected public deliverables
- authority limits
- execution constraints
- mode/stage constraints
- optional role-specific instructions
- source/provenance
- parent/derived role revisions
- canonical digest

角色標題本身不足以讓使用者判斷是否偏掉；GUI 與 chat 必須至少顯示 lens、為何被邀請、負責與不負責什麼，以及擁有的風險面。

本版維持兩層產品模型：MeetingRound/main 直接管理 RoleDefinitions。`PerspectiveAttempt` 只記錄某個 frozen role 的執行、retry 或 replacement，不構成第三層角色治理。meeting-plan v1 不新增 DepartmentRevision、部門權重或部門內權重。

### 為何不採三層 Department → Role 模型

這是刻意的產品決策，不只是為了縮小 schema：

- 部門權重再乘部門內角色權重，容易產生難以解釋的複合權重失真；數字最後可能反映組織結構，而不是本輪風險、證據與資訊價值。
- 真實會議裡，次席、資淺或非 leader 的參與者有時握有最可重現、最接近 runtime／使用者的證據。如果先由部門 leader 彙整成「部門立場」，這類少數意見可能在送達 main 前就被吃掉。
- 同部門角色因此各自保留 `role_id`、lens、risk ownership、public claim/evidence provenance，直接交由 main adjudicate；沒有 department consensus、department score 或 leader veto 的中介層。
- 席位數只表示 main 判斷該專業需要多少個真正不同的問題與證據來源，不構成投票加權。支持度較少但證據較強的角色仍可推翻同部門或全場多數意見。

這個設計模擬的是「老闆直接召集所需專業人士」：同一部門可以來一名或多名，但每個人都以自己的明確職責與證據對會議負責，而不是先被壓縮成部門代表的一票。

### Main 建議人數，使用者可調整

- Main 的初始完整 slate 同時就是席位建議；chat／GUI 可把 active roles 依 `department` 分組，顯示「Engineering：2 席」等衍生摘要。
- 不另存 `headcount`。角色 bindings 才是唯一真相，避免人數顯示與實際可執行角色不一致。
- 使用者要求增加人數時，main 以 `add`／`split` 產生不同 lens 的完整角色；若沒有新增資訊價值，應說明並拒絕複製席位。
- 使用者要求減少人數時，main 以 `remove`／`merge` 處理，逐步顯示 lineage、coverage delta，以及可能消失或被合併的次席證據來源。
- 每次人數調整都會建立新的 PlanRevision、重算 digest 並再次等待確認；人數本身不形成第三層 entity 或權重。

### 角色拆分複雜度三段

Main 在產生角色前先提出一個角色拆分 range；它回答的是「這次要把專業責任拆多細」，不是案件風險分數、固定人數級距或既定 roster。

| Range | 適用情境 | 角色拆分原則 |
| --- | --- | --- |
| `lightweight` | 邊界清楚、局部、可逆、低耦合，且沒有高後果風險 | 一般架構、資安、可靠性責任由能勝任的 generalist 一併承擔，不自動各設一席 |
| `standard` | 橫跨多種使用者、共享狀態、併發或外部整合 | 只拆出證據來源、權威或失敗後果確實不同的角色；專家席位需要具體理由 |
| `critical` | 財務／帳務、身份權限、敏感或受規管資料、不可逆 migration、安全、公開契約或高後果可靠性 | 無法安全合併的高後果證據由專門角色負責，但仍不以職稱湊固定名單 |

- Range 不改變 evidence、authority、safety 或 review gate；`lightweight` 不是降低標準。
- 使用者可以改 range。Main 必須重新計算完整 slate、coverage 與成本差異，建立新的 PlanRevision；不能只改標籤而保留原席位。
- 一個任務提到 API、資料或基本 auth hygiene，本身不足以自動邀請架構師或資安專家；應先判斷是否真的需要不同 evidence owner。
- 實際使用者 coverage 是另一個維度。跨多種操作目標、權限或失敗後果的 UI，即使是 `lightweight`，仍可需要多個精簡的 actual-user lenses；反之 `critical` backend work 不必硬加無關的使用者角色。
- 模擬 actual-user lens 先在未看設計解法時提出目標、資訊需求、可能誤解與不可接受失敗，再對已公開的 UI claims 做 bounded critique。其結果不可宣稱為真正使用者研究。

### 使用者操作

| 操作 | 語意 |
| --- | --- |
| accept all | 不修改 main 產生的 slate，直接確認並開始 |
| edit | 保留 `role_id`，產生新 revision |
| add | 建立新的 logical role |
| remove | 保留 tombstone 與 coverage delta，不靜默刪除歷史 |
| merge | 建立新 role，記錄所有 parent role revisions |
| split | 建立多個 child roles，記錄來源 revision |
| reset | 回到 main-generated revision，再次重算 coverage |
| import add | 以匯入 prompt 建立一個新 role draft |
| import replace | 用匯入內容修訂指定 role |
| import merge | 把匯入內容合併到指定 role 的角色層 |

Main 不得在使用者移除角色後偷偷把它加回去。若 critical coverage 被移除，應顯示缺口、最小修正建議與 gate effect；使用者可以明確承擔風險，但 uncovered 不會因此變成 covered，也不能得到 review `GO`。

## 外部角色 prompt 匯入

### 正確定位

```text
外部 ChatGPT／Claude 產生角色定位 prompt
  → 使用者貼入 skill
  → skill preview／normalize
  → 顯示 accepted、rewritten、ignored、conflicting 差異
  → 使用者套用到 draft
  → 產生新的 RoleRevision
  → freeze 後交給內部 fresh subagent 執行
```

這不是 live external participation，也不新增 `external executor`。

### 三層資料模型

1. `SourceArtifact`
   - 保存使用者提供的來源內容、user-declared origin、author/provider label、source reference、import time 與 raw digest。
2. `NormalizedRole`
   - 把來源內容映射到 canonical role fields，附 normalization warnings 與 field-level diff。
3. `EffectiveRole`
   - 使用者實際看到並確認、可由 skill 執行的完整 app-level 角色定義。

Raw imported text 不是較高層 instruction。它的合法角色內容會進入 EffectiveRole，但不得直接覆蓋 system/host/repository authority。

### 編譯優先序

```text
host / repository safety and authorization
  > meeting invariants
  > round authority packet and mode rules
  > EffectiveRole
  > public response contract
```

匯入內容不能：

- 把自己變成 moderator；
- 強迫特定結論或投票結果；
- 擴張 scope、authority、tools 或 external writes；
- 取得 peer findings 或 raw reports；
- 要求 hidden chain-of-thought、private scratch 或 raw transcript；
- 改寫 independence、verification、adjudication 或 output contract；
- 要求 live 呼叫原外部 provider。

### Conflict handling

應阻擋 freeze：

- authority/scope/tool expansion；
- moderator impersonation；
- forced conclusion；
- peer private material access；
- private-reasoning request；
- irrecoverable parsing failure；
- live external execution requirement。

應顯示 warning，但可由使用者確認：

- lens duplication；
- persona bias；
- excessive verbosity；
- unverifiable origin；
- weak evidence duties；
- critical coverage removal。

不得靜默刪除衝突文字。Invalid import 不改動目前 active draft。

### Raw prompt retention 決策

採用 privacy-preserving default：

- Raw source 只留在 access-controlled meeting draft/input record。
- EffectiveRole、provenance summary 與 raw digest 必須保留。
- 普通 panel result 與 standard share/export 不包含 raw source。
- Full-fidelity bundle 只有在使用者明確選擇 `include_source_text` 時才包含 raw source。

## 會議執行

### Independent opening

- 每個 frozen role 在 fresh internal context 形成第一份獨立立場。
- 所有角色收到同一 immutable authority/evidence snapshot。
- 在 opening 完成前，不提供 peer output、vote count 或 moderator preferred answer。
- Capacity 只影響 waves 與 latency，不改變已確認的角色 slate。

### Moderated deliberation

Opening 完成後，main 建立 public issue register：

- 正規化重複觀察但保留 provenance；
- 列出衝突主張、evidence locators 與未解問題；
- 對相關角色發送 bounded challenge/rebuttal packets；
- 只提供公開 claim 與 evidence，不轉交 raw peer reports；
- 針對重大衝突親自做 reproducible verification。

討論不是固定跑幾輪，而是在每個 material issue 已被 accepted、rejected、deferred、out_of_scope、needs_user_decision 或指定 unresolved owner/gate 後結束。

### Round close 與下一輪

關閉前必須：

- 記錄每個 execution attempt、wave、retry、replacement 與 failure；
- 對每個 critical surface 標記 coverage；
- 對 material issue 提供 disposition；
- 驗證重大證據或明確標示 unresolved；
- 重新比對 terminal condition；
- 產生 gate、next step 與 public handoff。

下一輪不得默認沿用 frozen slate。Main 必須：

- 將上一輪 public items 標記 `carry_forward`、`deferred`、`excluded` 或 `needs_user_decision`；
- 重新計算 risk surfaces；
- 重新產生完整角色 slate；
- 再次進入 user review/freeze。

## Contract architecture

### 分離 planning control plane 與 result projection

現有 `panel-output` v1.1 主要表示完成後的 perspectives、items、decisions、coverage、orchestration、gate 與 summary，不適合承載 editable draft。

建議新增獨立、platform-neutral 的 `meeting-plan` v1 contract：

- Meeting
- MeetingRound
- PlanRevision
- RoleRevision
- risk surfaces 與 coverage plan
- user adjustments/import provenance
- warnings/acknowledgements
- freeze metadata
- current state、allowed actions 與 events

現有 `panel-output` 保持 closed-round result。未來 `panel-output` 1.2 只做 additive immutable references：

- meeting/round identity
- frozen plan revision/digest
- role/role revision provenance
- risk surface IDs 與 planned role ownership

v1.0/v1.1 payload 必須繼續通過且被視為沒有 meeting-plan provenance 的 legacy results。

### 核心識別

| Entity | Identity purpose |
| --- | --- |
| Meeting | 完整會議目標 |
| MeetingRound | 一次 review-and-execution boundary |
| PlanRevision | 一份可確認的完整 draft/frozen plan |
| Role | 穩定部門 lineage |
| RoleRevision | 一份 immutable effective definition |
| PanelRun | 一次 round execution/result |
| PerspectiveAttempt | 一次 agent attempt/retry/replacement |

所有 immutable snapshots 使用 canonical serialization 計算 digest。`perspective_id` 不得取代 `role_id`。

### Validator

需要三層 validation：

1. meeting-plan schema/semantic validator；
2. panel-output v1.2 validator；
3. bundle validator，核對 frozen digest、role/risk references、attempt lineage、coverage ownership 與 final result mapping。

新增 v1.2 時要注意現有 semantic checks 對 `schema_version == "1.1"` 的精確判斷，不能只加 JSON Schema 欄位而漏掉 executor/GO assurance。

## GUI handoff

### GUI 必須能重建的狀態

- meeting objective、scope、authority summary；
- current round/state/state version；
- main 建議的 complexity range、selection reasons 與是否由使用者調整；
- main-generated roles 與 selection rationale；
- active PlanRevision 與 prior diff；
- role coverage、overlap、drift 與 import warnings；
- allowed actions；
- frozen plan/digest；
- queue、wave、attempt、retry、replacement、degradation；
- public issue register、verification、decisions、gate；
- next-round handoff。

Refresh 後必須能靠 public query state 完整重建畫面，不依賴重播 private agent messages。

### Commands

- `create_meeting`
- `regenerate_roles`（可帶 requested complexity range；必須回傳完整 slate／coverage／cost delta）
- `edit_role`
- `add_role`
- `remove_role`
- `merge_roles`
- `split_role`
- `reset_role_to_generated`
- `preview_import`
- `apply_import`
- `confirm_and_start`
- `cancel`
- `resume`
- `create_next_round`

所有 mutation commands 使用 expected revision/state version，必須 idempotent 或具明確 idempotency key。

### Public events

- `roles_generated`
- `plan_revision_created`
- `import_previewed`
- `role_slate_frozen`
- `run_phase_changed`
- `role_queued`
- `role_started`
- `role_completed`
- `role_failed`
- `role_replaced`
- `degradation_changed`
- `attention_required`
- `result_ready`
- `next_round_created`

### Stable error codes

- `STALE_DRAFT_REVISION`
- `INVALID_STATE_TRANSITION`
- `ROLE_SLATE_FROZEN`
- `CRITICAL_COVERAGE_UNACKNOWLEDGED`
- `IMPORT_EMPTY`
- `IMPORT_UNPARSABLE`
- `IMPORT_TOO_LARGE`
- `IMPORT_AUTHORITY_CONFLICT`
- `PLAN_DIGEST_MISMATCH`
- `RUN_NOT_RESUMABLE`

Domain codes 保持穩定且不本地化；GUI 用 structured parameters 產生 localized display text，不能只靠顏色傳達 warning/state。

### GUI 功能區，不預設視覺版型

1. Meeting brief：目標、scope、authority、mode，以及 main 建議的 complexity range 與理由。
2. Role proposal：main-generated role cards、邀請理由、coverage，以及依 active roles 衍生的各專業席位數；department 只作分組標籤。
3. Role adjustment：調整 range 或 edit/add/remove/merge/split/reset/import preview；range 改變時顯示完整 slate／coverage／cost delta。
4. Confirm and start：revision/digest、critical warnings、one-click start。
5. Meeting room：phase、waves、role progress、degradation、attention。
6. Decision board：summary/gate、accepted changes、risks、user decisions、evidence drill-down。
7. Next round：public handoff、recomputed risks、新的 generated slate。

## Compatibility 與 impact

| Surface | 預期變更 |
| --- | --- |
| `SKILL.md` | 在 selection 與 dispatch 之間加入 role generation/review/freeze；加入 meeting phases |
| `references/modes-and-selection.md` | 每個 round/stage 重新產生與確認 slate；補 handoff |
| `references/panelist-protocol.md` | 擴充 RoleDefinition、EffectiveRole 與 ExecutionEnvelope |
| `references/authority-and-fallback.md` | freeze、coverage acceptance、post-freeze change、round recovery |
| adapters | host-specific confirmation/yield、resume、events、fresh dispatch mapping |
| meeting-plan 1.1 schema | draft/revision/import/freeze/control state，以及 digest-bound complexity profile；保留 1.0 input 相容性 |
| panel-output 1.2 | additive meeting/round/role provenance references |
| validators | meeting-plan、v1.2、bundle cross-document invariants |
| tests/evals | multi-turn confirmation、import、freeze、GUI state、compatibility |
| README/metadata | 正確描述 boss-led meeting flow 與 GUI status |

## Meeting core 驗收條件

Meeting core 只有在下列條件都通過後才算完成，才能把狀態升級為 GUI-ready：

1. Main 在每輪先產生完整角色 slate；沒有要求使用者從空白開始。
2. Main 顯示建議的 complexity range 與理由；使用者不修改即可一鍵確認，也能調整 range 或 edit/add/remove/merge/split/reset/import。
3. 外部 prompt 只改角色層，不能變成 external executor 或覆蓋 invariants。
4. 所有修改建立 immutable revision，stale confirm 與 digest tampering 被拒絕。
5. Freeze 後角色不可原地修改；retry 使用相同 role revision。
6. Independent opening 不看 peer findings；deliberation 只交換 public claims/evidence。
7. Critical coverage loss 有警示、acknowledgement 與 gate effect。
8. Meeting-plan 1.1、panel-output 1.2 與 bundle validators 通過 positive/negative fixtures，meeting-plan 1.0 保持相容。
9. v1.0/v1.1 fixtures 與 consumers 保持相容。
10. Neutral multi-turn eval 覆蓋 generated-first、全部 role operations、external prompt import、freeze、waves/fallback、next round reselection。
11. Fresh forward eval 證明 role review/freeze 不是人工模擬，且 final execution 使用使用者確認的 exact digest。
12. `python3 scripts/validate_repo.py` 與 Skill Creator validation 全數通過。
13. Neutral range cases 證明 bounded work 不自動加入架構／資安／可靠性專席，standard work 只拆 evidence-distinct lenses，critical work才為無法安全合併的高後果證據配置 specialists。

## 進入 GUI 的 gate

GUI 不應直接建立在只描述 final result 的 panel-output schema 上。下一階段開始 GUI 前，至少要有：

- 已實作並 forward-tested 的 meeting lifecycle；
- meeting-plan v1 schema 與 validator；
- role import/normalization/freeze runtime；
- GUI 所需 queries、commands、events、errors；
- panel-output 與 frozen plan 的可驗證 reference；
- 一份可重播的 neutral demo meeting fixture。

達成後，GUI 階段只需要實作既定 domain 行為與 progressive-disclosure interaction，不再重新決定 skill 的核心產品語意。
