# 多視角編排邏輯現況評估與發展建議

- 評估日期：2026-08-26
- 基線：`main` / `dd12b4df27d146da2dd34a98058b2d4be758df27`
- 評估模式：`review`
- 工作樹基線：乾淨
- 驗證基線：`python3 scripts/validate_repo.py` 通過，59 個單元測試全數通過

> 2026-08-28 現況更新：本文主體保留 2026-08-26 的歷史 baseline 與當時缺口。後續 meeting core 已完成 portable runtime、meeting-plan v1.0、panel-output v1.2、semantic/bundle validators 與 105 個 deterministic tests；Codex v1.1 fresh release scorecard 為 `GO`，21/21 cases、49 個公開回合及 95/95 fresh blind assertions 全數通過。這滿足 meeting-core 的 GUI entry gate，但 GUI 尚未實作，Claude Code 仍只有 structural status。

> 2026-08-29 現況更新：三組 ordinary-session／meeting-skill 盲評顯示效益具有條件性，並促成 `lightweight`／`standard`／`critical` 角色拆分 range、actual-user lens protocol 與 meeting-plan v1.1。這些 runtime bytes 尚未由新的完整 release scorecard 綁定，因此 2026-08-28 的 `GO` 現為歷史證據，current-runtime GUI entry gate pending。比較結果見 [Meeting core 規劃品質對照評估](evaluations/meeting-core-quality-comparison.zh-TW.md)。

> 2026-08-31 產品與證據更新：核心效果已進一步限縮為「先用 Main＋領域專業＋End user 改善使用者任務與 UIUX Plan，再交給普通 Agent 進入 Spec／implementation」。第一個 plan-only Pilot 由三位 fresh 模擬租戶一致選擇 Treatment，平均高 `+0.604/5`；流程 gate 通過，但單案只屬方向性訊號，仍待 N-task 驗證。詳見 [Meeting core 使用者驗證 Plan Pilot](evaluations/meeting-core-user-validated-plan-pilot.zh-TW.md)。先前 technical plan／spec 實驗保留為次要機制證據。

> 2026-08-31 N-task 更新：六案 plan-only 批次已完成。標準 Treatment 在 5/6 任務勝出，18 位 fresh 模擬使用者 evaluator 中 13 位偏好 Treatment，平均差 `+0.222/5`；最大改善是避免過度設計 `+0.583`，但 recovery 平均退步 `-0.194`。結果支持依使用面、交接與狀態後果動態 routing，不支持每案必開會或更多席位必然更好。詳見 [Meeting core Plan-only 六案盲評](evaluations/meeting-core-plan-only-batch6.zh-TW.md)。GUI 前仍須先更新 selective routing／recovery closure 並完成 current-runtime behavioral release validation。

## 結論

目前的核心方向是成立的，而且成熟度高於一般「叫多個 Agent 各自發言」的做法。它已經形成一條清楚的控制鏈：先界定目標、授權與權威，再依風險面動態選角，以 fresh context 保持獨立，最後由 moderator 依證據裁決，而不是投票。失敗、容量不足、replacement 與 single-session fallback 也都有公開且可驗證的降級語意。

整體評估為 `REVISE`，不是因為 read-only panel 不可用，而是現況尚不足以完整支持三項更強的宣稱：

1. `full_cycle` 能公開說明每個 stage 之間如何收斂與交接；
2. 有編輯授權時，能持續執行 edit → test → impact review → fresh follow-up，直到 terminal condition 真正成立；
3. machine-readable `GO` 與 release scorecard 能證明語意正確，而不只是結構、雜湊與自填狀態一致。

因此可以把現況理解成：

| 使用情境 | 現況判斷 |
| --- | --- |
| 單階段 `ideate` / `design` / `converge` / read-only `review` | 成熟可用 |
| 容量不足、timeout、replacement、subagent unavailable | 規則完整，降級揭露良好 |
| `full_cycle` 的 stage handoff | 可執行，但公開裁決鏈不完整 |
| 授權後持續修正到 terminal condition | 有局部指令，尚未形成閉環 |
| v1.1 public contract 的結構與相容性 | 強 |
| `GO` 的 resolution/verification 語意 | 需補強 |
| Codex 行為證據 | 廣，但部分旗艦案例是 degraded fallback |
| Claude Code 行為證據 | 尚未建立；目前只有結構相容性 |

## 已確認的產品主軸

使用者已確認下一階段要把 skill 強化為「老闆召集式多視角會議」：main 每輪自行決定要找幾個部門、完整產生角色定義，使用者可以直接接受、調整，或匯入由外部 ChatGPT／Claude 產生的角色定位 prompt；凍結後仍由 skill 內部 fresh subagents 執行。

外部模型是 prompt authoring source，不是 live meeting executor。完整設計與 GUI handoff 見[老闆召集式多視角會議核心設計](boss-led-meeting-core-design.zh-TW.md)。

> 2026-08-28 實作更新：此方向已完成 Codex release validation。21 個 neutral multi-turn cases 以 fresh isolated contexts 執行，三組未接觸修正歷史的 graders 對 95 條 assertions 全數判定通過；machine-readable GUI case 亦通過 meeting-plan、panel-output 與 bundle validators。本文的原始現況評估仍保留為 baseline，不應用來描述目前 meeting-core behavioral status。

## 評估範圍與方法

本次檢查涵蓋：

- runtime：[`SKILL.md`](../SKILL.md)、[`adapters/codex.md`](../adapters/codex.md)、[`references/`](../references/)；
- public contract：[`schemas/panel-output.schema.json`](../schemas/panel-output.schema.json)、[`schemas/stable-enums.v1.json`](../schemas/stable-enums.v1.json)；
- deterministic checks：[`scripts/validate_panel_output.py`](../scripts/validate_panel_output.py)、[`scripts/validate_repo.py`](../scripts/validate_repo.py)；
- compatibility 與 invariant tests：[`tests/`](../tests/)；
- forward evidence：[`evals/cases.json`](../evals/cases.json)、Codex scorecard 與 captured public artifacts。

評估採三個互不重疊的 fresh-context 視角：

- 編排與決策品質：控制流程、獨立性、stage boundary、terminal condition；
- 契約與可靠性：schema、semantic validator、fallback、release/eval assurance；
- 使用者與演進性：觸發、可讀性、採用成本、跨平台與產品 roadmap。

所有高嚴重度發現都由 moderator 直接讀取原始檔案或用 validator probe 重現。本文只保留公開觀察、證據、判斷與建議，不包含 panelist 原始報告或私有推理。

## 現行邏輯

```text
使用者目標
  → 選擇最窄 mode
  → 建立 authority packet 與授權邊界
  → 建立 risk-surface map
  → 動態選出最小且互異的 lenses
  → 載入單一 host adapter，配置 model / slots / waves
  → fresh-context panelists 獨立取證
  → moderator 正規化、親自驗證、依證據裁決
  → 必要時由 main session 編輯、測試、focused follow-up
  → 產生單一 synthesis；需要時輸出 v1.x public contract
```

### 1. 入口與 mode

`SKILL.md:10-20` 強制只選一個入口模式，並要求用最窄模式完成任務，避免普通 code review 被不必要地升級成 panel。五種模式各自有不同的起始材料、diversity 行為、輸出與 gate；`full_cycle` 不是預設值。

這個切法是正確的。它把「發散」、「具體化」、「有限集合裁決」與「readiness review」分開，降低 ideation 被過早排名、design 被直接當成 implementation、review 被誤當投票的風險。

### 2. Authority 與 scope

`SKILL.md:22-32` 與 `references/authority-and-fallback.md:5-24` 要求先確認 repository、branch、revision、dirty work、產品決策、契約、runtime、tests 與授權。權威衝突按各自 remit 解決，不使用「文件永遠高於 runtime」之類的單一排序。

這是目前最穩固的部分之一。Panel 不會擴大使用者授權，dirty work、外部寫入、destructive action 與產品決策 gate 都有明確界線。

### 3. 動態選角

`SKILL.md:34-46` 先建立 risk-surface map，再選角色；`references/modes-and-selection.md:77-94` 用 distinct question、distinct evidence、stakeholder impact、high-risk ownership 與 marginal value 五個測試決定是否保留 lens。

它的關鍵價值是「風險先於職稱」。App、API、security、finance 或 end customer 都只是候選 lens，不是固定席次。這能減少角色重疊，也能在 accounting、identity、authorization、migration、不可逆資料或外部承諾真正重要時給予專責視角。

### 4. 獨立執行與容量治理

`SKILL.md:48-81`、`adapters/codex.md:10-31` 與 `references/model-and-execution-policy.md:43-61` 要求：

- 每個 panelist 使用 fresh context；
- 所有人收到相同 authority packet，但只有一個獨特 lens；
- 不洩漏其他 panelist 的發現、moderator 偏好或預期缺陷；
- main session 保留為 moderator；
- slots 不足就跑 waves，不刪 lens；
- timeout 最多 retry 一次，replacement 保留相同 lens；
- subagent 不可用時，明確標示 single-session fallback 與 reduced independence。

這些規則能有效區分「多段角色扮演」和真正獨立的多上下文評估，並避免把 model diversity 誤當 perspective diversity。

### 5. 裁決與最終責任

`SKILL.md:93-105` 要求 moderator：

- 合併重複觀察，但保留衝突提案；
- 親自驗證 blocker/high、產品方向變更與強證據衝突；
- 不以 reviewer 數量作為真實性依據；
- 使用 `accepted`、`rejected`、`deferred`、`out_of_scope`、`needs_user_decision`；
- 只把真正的產品、scope、外部承諾、destructive 或權威衝突升級給使用者。

這使 moderator 成為最終 accountable owner，而不是 panel report 的轉寄者。少數但可重現的 runtime evidence 可以推翻沒有證據的多數意見，是此設計最重要的品質保證。

### 6. Public contract 與 fallback 可稽核性

v1.1 schema 記錄 perspectives、items、decisions、coverage、execution mode、waves、failure、replacement、gate 與 summary。Semantic validator 另外檢查：

- ID 唯一與 reference integrity；
- evidence-backed coverage；
- completed/failed/replaced 狀態模型；
- replacement graph、順序與同 lens/stage；
- subagents/waves/mixed/fallback 與 executor 一致；
- `full_cycle` 的 stage 完整性與順序；
- `GO` 不可有 vacuous panel、未覆蓋 critical surface 或 blocker/high item；
- prohibited private-reasoning keys。

現有 59 個單元測試和 digest-bound eval artifacts 對這些結構與 provenance 提供了很強的回歸保護。

## 主要優點

### 動態而非固定 roster

角色數量不預設最小值或最大值，由問題風險和新增資訊價值決定。這比固定「產品、工程、設計、QA」更節制，也更能處理 accounting、authorization 等高後果表面。

### 證據而非投票

Panelist conclusion 只是裁決輸入；moderator 必須驗證重大主張。這直接降低群體共識、權威偏誤與多數幻覺。

### 獨立性與降級誠實

fresh context、相同 authority packet、禁止互相看到 findings、waves 不洩漏前波結果，構成可操作的獨立性規則。無法獨立執行時，不會把 main-session lens passes 包裝成獨立 panel。

### Scope 與 dirty-work 保護

Panel 不擴張授權；read-only、editable artifacts、外部寫入與 destructive actions 分開處理。Repository authority、branch 和 unrelated work 都有保護規則。

### Public-only audit model

輸出只保留觀察、證據、提案、決策與簡短 rationale，明確排除 chain-of-thought、private scratch 與 raw transcripts。這讓 GUI/API 能做到 drill-down，又不依賴不可公開的內部推理。

### 失敗路徑不是附註

capacity、timeout、tool error、replacement、mixed execution 與 subagents unavailable 都是正式 contract 的一部分；coverage 和 gate 會隨降級結果調整，而不是只在文字結尾補一句免責聲明。

## 主要缺口

### F-01 — `full_cycle` 缺少明確 stage handoff（High）

已驗證事實：`references/modes-and-selection.md:65-75` 規定每個 stage 要關閉公開 artifacts、重新選 lens，但沒有規定 divergent ideation candidates 如何被帶入 design。`evals/artifacts/full-cycle-reselect-lenses.json` 中 ideate 保留四個未排名候選，design 卻直接進入 scheduling/hold 解法，沒有逐項說明 carry forward、defer 或 exclude。

影響推論：moderator 可能在 stage boundary 隱含做出產品方向選擇，繞過真正的 user decision gate，且事後難以稽核為何只設計某一候選。

建議：在每個 full-cycle boundary 加一份公開 handoff：

- 上一階段輸入項；
- `carry_forward`、`deferred`、`excluded` 或 `needs_user_decision`；
- 依據的 authority/evidence；
- 下一階段的 bounded input 與 non-goals。

Ideate 本身仍不排名；handoff 是 stage transition 的裁決，不是回頭改寫 ideation。

### F-02 — Terminal condition 與 authorized correction 尚未閉環（High）

已驗證事實：`terminal_condition` 會進入 authority packet，`SKILL.md:102` 也要求 material correction 後做 focused fresh-context follow-up；但最終輸出前沒有通用的 terminal-condition re-audit，也沒有明確迭代規則。現有 17 個 eval 也沒有授權修改工作樹並驗證 edit → test → re-review 的案例。

影響推論：Agent 可能在完成一次修正或 synthesis 後停止，即使 affected consumers、tests 或 follow-up review 尚未讓 terminal condition 成立。

建議：把 moderator exit invariant 寫清楚：

```text
adjudicate
  → authorized edit
  → targeted tests / runtime verification
  → recompute affected risk surfaces
  → fresh follow-up for affected lenses
  → compare actual result with terminal_condition
  → complete，或以 revise / no_go / blocked 明確退出
```

同時將 authority packet 的 `artifacts` 拆成 `read_only_artifacts` 與 `editable_artifacts`；read-only panelist 的 editable list 必須為空。

### F-03 — `GO` 無法同時保留已駁回或已修正的高風險歷史（High）

> 2026-08-27 candidate resolution：meeting core 採用下述短期相容策略並已寫入 runtime/contract。發現 blocker/high 的 round 必須保留原 finding 並以 `revise`/`no_go` 關閉；修正後另開重新選角、review/freeze 的 verification round，只有新一輪能依 fresh evidence 發出 `go`。因此沒有改寫 v1.0/v1.1 既有 validator 語意，也不會為取得 `GO` 刪除歷史。

已驗證事實：`SKILL.md:105` 的規則是沒有「未解決」的 blocker/high 才能 `GO`；但 `scripts/validate_panel_output.py:520-532` 會阻擋任何 blocker/high item，且 line 527 建立的 `unresolved` set 沒有參與判斷。實際 probe 把 blocker decision 設為 `rejected`、清空 unresolved list 並設 gate=`go`，validator 仍回傳 `gate is go with blocker item I1`。

影響：錯誤的 high finding 即使被 moderator 以證據駁回，也會永久阻擋同一 payload 的 `GO`。Producer 可能被迫刪掉原始 finding，與 public/auditable 原則衝突。已修正後的 high finding 也沒有 verification/resolution 狀態可表達。

建議：

- 短期：修正後啟動一個新的 review run，保留舊 payload，不在同一 v1.1 payload 中刪除歷史以取得 `GO`；
- 下一個 additive minor：加入 resolution/verification provenance，明確區分 `rejected`、`resolved_and_verified` 與 unresolved；
- 只讓 unresolved 或仍具負面效力的 high/blocker 阻擋 `GO`；
- 增加 rejected-high、resolved-high、accepted-unresolved-high 的 compatibility tests。

若改動現有欄位語意會破壞 v1 consumer，應保留 v1.0/v1.1 行為，透過 v1.2 additive fields 啟用新語意；不要靜默改寫 1.x contract。

### F-04 — Release eval 保證 provenance，但沒有驗證 assertion 真偽（High）

已驗證事實：`scripts/validate_repo.py:341-411` 會核對 assertion 名稱、填寫狀態、artifact digest、prompt/runtime/suite revision，並由自填 assertion statuses 推導 case 與總 gate；它沒有將 assertion evidence 與 `artifact.output` 做語意比對。`tests/test_validate_repo.py:97-129` 使用固定字串 `Captured public moderator response for test validation.`，仍可作為 passing artifact；`schemas/eval-artifact.schema.json:31` 對 output 只要求至少 16 字元。

影響：目前 release gate 很能證明「這份 scorecard 綁定這次輸出且內部一致」，但不能單靠 deterministic validator 證明「輸出真的符合 assertion」。錯誤或自我偏誤的人工評分仍能得到 `GO`。

建議：

- 把 assertion 分成 machine-checkable 與 qualitative；
- mode/gate/schema/fallback/word budget 等由 deterministic checker 直接從 output 驗證；
- qualitative assertion 記錄 verifier identity、method、evidence locator 與獨立性；
- 重要 release case 由不同於 runner 的 fresh evaluator 評分；
- release gate 顯示 structural integrity 與 behavioral assurance 兩個維度，不把兩者混為一談。

### F-05 — 自然語言 mode 規則尚未完全進入 semantic validator（Medium）

已驗證 probe：

| Payload 變更 | `semantic_errors` 結果 |
| --- | --- |
| `run.mode=ideate`、`gate.state=go`、移除 blocker severity | `[]` |
| `run.mode=review`、`gate.state=continue` | `[]` |
| review run 的所有 perspective/item/decision `stage=design` | `[]` |
| `failure.retry_count=7` | `[]` |

這與 `references/modes-and-selection.md:7-13` 的 normal gate matrix、單一 mode 的 stage 語意，以及 `SKILL.md:112` 的最多一次 retry 有落差。

建議：為 producer 加入 mode ↔ gate、single-mode ↔ stage、retry policy 的 semantic tests。由於更嚴格的規則可能改變既有 payload validity，應先定義 v1.0/v1.1 相容策略；較安全的做法是在 v1.2 對新 producer 啟用，保留舊 payload 的讀取能力。

### F-06 — Critical coverage 只驗證「有 evidence」，未綁定正確 lens/surface（Medium）

已驗證事實：coverage 的 `risk_surface` 與 `lens` 是 free string，只有 `evidence_item_ids`，沒有 perspective ID。Validator 會確認 item 存在、有 evidence、來源 perspective 已完成，卻不驗證該 item owner 就是 coverage 宣稱的 lens，也無法機械判斷 evidence 是否對應該 risk surface。

影響：不相關的 completed-perspective evidence 在結構上可以替任意命名的 critical surface 建立 covered 狀態，進而影響 `GO`。

建議：v1.2 可加入 coverage perspective provenance，檢查 evidence owner、replacement chain 與 declared lens 一致。Chat-only review/full-cycle 則至少回報 critical surface、owner lens、covered/partial/uncovered、evidence 與 gate effect，避免只列「選了哪些角色」。

### F-07 — 預設輸出與 onboarding 還不夠節制（Medium）

已驗證事實：README 有架構、安裝和驗證說明，但缺少從自然語言 request 到 result 的快速範例。Full-cycle artifact 在使用者要求 concise 時仍有 1,072 個英文單字；明確限制 220 words 的 converge artifact 則以 204 words 保留了 decision、rejection rationale、risk 與 next step。

影響：新使用者不容易判斷何時該用 panel、如何指定 scope/authorization，以及會得到什麼格式；full-cycle 結果也可能正確但難以掃讀。

建議：

- README 增加「60 秒開始」與 when-not-to-use；
- 每個 mode 提供一個最小 prompt；
- chat 預設使用 progressive disclosure：headline/gate → decisions → top risks → user gates → next step；
- 只有使用者要求時展開 stage/evidence detail；
- 所有宣稱 concise 的 eval 都要有可驗證 budget，而不只 converge case。

### F-08 — 行為證據的 independence 與 host 覆蓋不均（Medium）

已驗證事實：Codex scorecard 的 17 cases 全數通過，但 full-cycle、部分 high-risk review 與 positive trigger 案例的 notes 明確標示 main-session fallback 或 reduced independence。README 也誠實標示 Claude Code 只有 structural compatibility，尚未有 behavioral scorecard。

影響：fallback 正確性證據很強，但每個 promoted mode 的 non-degraded independent execution 證據不一致；跨 host 宣稱也還不能擴大。

建議：release matrix 分開呈現 functional pass、independent-subagent assurance、degraded fallback coverage 與 host。每個 promoted mode 至少保留一個 non-degraded fresh-subagent run；Claude 完成獨立 scorecard 後再升級 behavioral status。

## 建議優化順序

| 優先序 | 項目 | 主要產出 | Public contract 影響 |
| --- | --- | --- | --- |
| P0 | Boss-led meeting control plane | main-generated roles、user review/import、freeze、round lifecycle | 新 meeting-plan v1；panel-output 後續 additive reference |
| P0 | Full-cycle stage handoff | runtime rule、handoff template、neutral eval | Chat 可先不改 schema；machine record 建議 v1.2 additive |
| P0 | Terminal-condition closure | exit invariant、editable/read-only artifacts、mutation eval | 可先只改 runtime/eval |
| P0 | Resolution-aware `GO` | resolution/verification model、compatibility tests | 建議 v1.2 additive；避免改寫 v1.1 意義 |
| P0 | Eval assurance split | deterministic assertion checkers、independent qualitative verifier | eval schema 需版本化；不影響 panel-output schema |
| P1 | Mode/stage/gate/retry semantics | semantic matrix 與 negative tests | 需先定義舊 payload 相容策略 |
| P1 | Coverage provenance | perspective binding、chat coverage reconciliation | v1.2 additive |
| P1 | Progressive disclosure | chat output template、word/detail budgets、quick start | 無需 public schema 變更 |
| P2 | Assurance matrix 與 locale cases | 每 mode 非降級案例、zh-TW trigger/mode eval | eval suite 版本更新 |

建議先完成 boss-led meeting control plane 與 terminal-condition closure，再把 stage handoff、resolution-aware `GO`、verification provenance 和 coverage provenance 一起納入 versioned contract proposal，避免 GUI 建立在不完整的 final-result schema 上，也避免連續小改造成 consumer 負擔。

## 未來可開發方向

### 1. Public verification 與 stage-transition layer

下一個 contract minor 可增加：

- stage transition 的 carry-forward/defer/exclude 公開記錄；
- moderator verification 的 evidence、method、result 與 verified item；
- finding resolution、修正版本與 follow-up reviewer；
- coverage 到 perspective/replacement chain 的 provenance；
- 新 run 對前一 run 的 supersede/follow-up reference。

這些都是 public rationale 與 provenance，不是 hidden chain-of-thought。

### 2. Reference renderer / CLI / API consumer

現有 schema 已足以建立一個薄型 reference consumer：

- 先跑 `validate_panel_output.py`；
- 預設顯示 summary、gate、accepted changes、remaining risks、user decisions；
- drill down 顯示 perspectives、evidence、coverage、adjudication 與 degradation；
- 對同 major 的未知欄位或 enum 使用安全 fallback；
- locator 只有通過 scheme/access policy 後才做成連結。

它能驗證 schema 是否真的適合 GUI/API，而不必先建完整產品。

### 3. Cross-host behavioral parity

先使用現有 neutral suite 建立 Claude Code 的 fresh-context scorecard，再補 host-specific capability case。Host 狀態應維持三層：structural、behavioral-degraded、behavioral-independent，避免用 Codex pass 推論其他 host。

### 4. Domain risk profiles

可建立可選的公開 profile，例如 identity/authorization、accounting、migration、privacy/security、mobile offline、external API。Profile 應提供：

- candidate risk surfaces；
- 必要 authority/evidence 類型；
- criticality 的預設建議；
- 常見 consumer 與 failure mode；
- 不應自動做出的產品決策。

Profile 只協助 risk discovery，不固定角色，也不能取代 dynamic selection。

### 5. Evidence snapshot 與 assurance tooling

為同一 run 建立不可變 authority/evidence snapshot（revision、digest、time、access boundary），讓不同 panelists 在不共享 findings 的前提下讀取同一證據基線。再逐步加入可重現 probe、deterministic assertion、independent evaluator 與 stale-evidence 提醒。

這能降低 waves 之間的基線漂移，也能讓「少數但可重現的 evidence」更容易被 moderator 查證。

### 6. Cost、latency 與輸出遙測

在不設定固定 roster 上限的前提下，記錄每個 lens 的執行時間、wave、degradation、是否產生新資訊、重複率與最終採納狀態。用這些資料校準 marginal-value stop rule、model routing 與 progressive disclosure，而不是依 panelist 數量判斷品質。

遙測只記錄公開 operational metadata，不保存 raw transcripts 或 private reasoning。

## 建議驗收條件

近期優化完成時，至少應滿足：

1. Full-cycle artifact 對每個 stage transition 都有公開 disposition，且 ideate 仍保持不排名。
2. 一個 neutral mutable-workspace eval 能證明授權邊界、dirty-work 保護、edit/test/follow-up 與 terminal-condition closure。
3. `GO` 可保留 rejected/resolved high finding 的公開歷史，同時仍阻擋真正 unresolved high。
4. Mode、stage、gate、retry 與 coverage provenance 有 negative tests。
5. Release gate 明確區分 artifact integrity、deterministic behavior 與 qualitative independent verification。
6. 每個 promoted mode 至少有一個 non-degraded fresh-subagent behavioral run。
7. Chat 結果預設可快速掃讀，詳細 evidence 以 progressive disclosure 提供。

## 本次驗證紀錄

- `python3 scripts/validate_repo.py`：通過；59 tests passed。
- 手動 semantic probes：確認 mode/gate、single-mode stage、retry count 與 rejected-high `GO` 目前未形成一致閉環。
- Captured artifact 檢查：確認 full-cycle stage handoff 未公開、concise 請求為 1,072 words；220-word converge case 則為 204 words。
- Scorecard 檢查：確認 Codex 17 cases 全數 pass，但部分 flagship/high-risk 路徑使用 disclosed main-session fallback；Claude 尚無 behavioral scorecard。

### 2026-08-28 meeting-core release 驗證

- `python3 scripts/validate_repo.py`：通過；105 tests passed。
- Fresh Codex batch：21/21 cases、49/49 public turns、0 runner failures。
- Fresh blind grading：三組 graders 分別覆蓋 cases 1–7、8–14、15–21，合計 95/95 assertions passed。
- Machine checks：meeting-plan v1.0、panel-output v1.2、bundle validation、220-word budget、stale/executed digest equality 與同專業多角色 evidence-ledger provenance 全數通過。
- Release evidence：[`evals/results/codex-2026-08-28.json`](../evals/results/codex-2026-08-28.json) 與 21 份 digest-bound public artifacts；舊 2026-08-10 scorecard 僅保留為 historical evidence。

這份文件只評估現況並提出方向，未修改 runtime、schema、validator、tests、eval artifacts 或安裝內容。
