# Meeting core 規劃品質對照評估

英文原版：[meeting-core-quality-comparison.md](meeting-core-quality-comparison.md)

後續 3–4 人壓縮實驗：[meeting-core-compact-panel-comparison.zh-TW.md](meeting-core-compact-panel-comparison.zh-TW.md)

- 評估日期：2026-08-29
- 評估範圍：GUI 實作前的規劃品質，不是 implementation 品質
- 狀態：比較實驗已完成；報告保留正向、中性與負向結果

## 評估問題

對於具有兩種以上實際使用者接觸面的中小型任務，老闆召集式多視角 meeting skill 所產生的 plan 或 spec，是否實質優於一般單一 session 的規劃結果？

實驗刻意包含一項預期效益偏低的任務。可信的結果不要求 meeting skill 在每一案都勝出。

## 評估方法

三個任務都各自規劃兩次：

1. 一個 fresh 的一般規劃 session，不使用 meeting skill，也不使用 subagent；
2. 一個 fresh 的 meeting-skill run，由 main 先產生完整角色 slate，經使用者檢查後才 freeze 並執行。

本次實驗中，使用者沒有修改個別角色定義，但在執行前發現一項系統性缺口：原始提案只有專業決策角色，缺少真正的終端使用者視角。Main 因此修訂三份 slate、重新展示，並且只在使用者明確核准後執行。

完成的規劃結果以候選 A／B 匿名處理。三位 fresh judges 各自獨立評估兩個候選，並針對下列八個維度給予 1–5 分：

- 需求覆蓋度；
- 多使用者工作流程；
- domain／state 一致性；
- 失敗恢復能力；
- contract 可實作性；
- UI 可操作性；
- scope 與假設紀律；
- 精簡度與資訊密度。

Judges 被明確要求不得因篇幅或複雜度而加分，並應扣除無權威依據的政策、矛盾、過度設計與未關閉狀態。他們不知道候選來源、預期勝方、repository 歷史或預定修正方向。

## 任務與結構性成本

| 任務 | 實際使用者接觸面 | Meeting 角色數 | 執行 waves | 納入原因 |
| --- | --- | ---: | ---: | --- |
| 候補名單自動遞補 | 公開客戶、第一線行事曆操作員、CMS 操作員 | 7 | 6 | 共享容量、逾時、通知與跨介面狀態 |
| 出貨前修改地址 | 客戶、倉儲操作員、CMS 客服 | 8 | 6 | 實體／數位狀態收斂與物流商交接 |
| CRM CSV 聯絡人匯入 | Workspace 管理員與受影響的 CRM records | 4 | 3 | 預期 meeting 效益有限的有界流程 |

每個 baseline 只使用一個規劃 session。Meeting run 另外需要角色產生、human review checkpoint、獨立視角與綜合裁決。本次沒有量測精確 token 與 wall-clock 成本，因此報告只以席位、waves 與互動階段作為結構性成本指標，不虛構數值成本比。

## 盲評結果

下表分數為三位 judges 在八個評估維度上的總平均。

| 任務 | 一般 session | Meeting skill | Skill 差值 | 配對偏好 | 實務差距 |
| --- | ---: | ---: | ---: | --- | --- |
| 候補名單自動遞補 | 4.542 | 4.958 | +0.416 | skill 3、一般 0 | 三位皆為小幅 |
| 地址變更 | 4.625 | 4.458 | -0.167 | skill 1、一般 2 | 三位皆為小幅 |
| CSV 匯入 | 4.833 | 4.708 | -0.125 | skill 0、一般 2、平手 1 | 小幅或無差異 |

因此 meeting skill 只在三案中的一案展現可重複的提升，並非普遍提高品質。所有配對的實務差距都不大。

## 各案發現

### 候補名單自動遞補：一致提升

Meeting 結果更清楚地建立 HOLD、BOOKING 與 BLOCK 共用的容量權威，也把通知投遞狀態與客戶接受邀請的業務權利分開，因而產生較安全的跨介面 UI 與恢復語意。

一般規劃結果本身已經很強，但它一方面把某個逾時結果視為 terminal，後文卻又暗示客戶可能繼續留在候補名單；同時也在權威不足時先固定 FIFO 與 30 分鐘期限。多視角在這案找出了單一 planner 沒有完全關閉的共享狀態歧義。

### 地址變更：覆蓋更多，關閉較弱

Meeting 結果增加了有價值的實體作業細節，包括標籤操作 attempts、物流商晚到 callbacks、包裹／標籤不一致處理，以及客戶、倉儲、客服視角對 UI 的檢查。

但它也引入更大的 state machine 與未經授權的政策。特別是：部分 placed／allocated 狀態被自動套用；同一個 `applied` 狀態混合了權威地址提交與物流商／HOLD 收斂；而且沒有完全關閉所有已建立標籤後的例外。兩位 judges 因此偏好較簡單的一般規劃，因為較小的模型在內部更完整閉合。

這是最清楚的反例：當每個 specialist seat 都增加狀態或政策，而 synthesis 沒有積極刪除或解決它們時，更多角色反而可能降低品質。

### CSV 匯入：如預期效益有限

兩個候選都很強。一般規劃對 Email-based update、外部 reference 與 rollback 稍微更精確；meeting 結果的政策紀律較好，也提出有用的 server cursor 概念，但額外流程沒有形成顯著的實務優勢。

這個良性負向對照符合預期：一個有界、可逆，而且只有一位主要操作員的流程，不會因為加入廣泛的專業 panel 就自動變得更好。

## 實際使用者視角的發現

Product、architecture 與 security 角色不能取代真正執行或承受工作流程結果的人。加入 actual-user lenses 後，對文字、資訊出現時機、可能誤操作，以及實體／數位不一致的檢查都有改善。

有效的 protocol 分成兩個階段：

1. 在看到 UI 提案前，模擬使用者視角先提出目標、資訊需求、可能誤解與不可接受的失敗；
2. 專業角色發布 bounded UI claims 後，由同一個 frozen user lens 只針對這些 claims 檢查可用性與誤操作風險。

這些只是模擬視角，不是訪談、telemetry 或使用者研究。模擬角色彼此同意，不能被報告成市場證據。

## 根因與產品決策

變更前的 selector 會因為任務出現一般架構、資料、authentication 或 reliability concern，就建立獨立 specialist seats。這讓小型任務看起來像需要高階組織會議，也增加 synthesis 負擔。本次實驗中的 7 席與 8 席 slate，對任務規模而言確實過重。

修正方式是加入三段角色拆分 range：

| Range | 選擇訊號 | 預設拆分行為 |
| --- | --- | --- |
| `lightweight` | 局部、可逆、低耦合，沒有高後果 trigger | 一般 architecture／security／reliability 責任由能勝任的 generalist 合併負責 |
| `standard` | 多個使用者接觸面、共享狀態、併發或外部整合 | 只拆出 evidence、authority 或失敗後果確實不同的 lenses |
| `critical` | 財務／帳務、身份、敏感或受規管資料、不可逆 migration、安全、公開 contract 或高後果 reliability／security | 無法安全合併的高後果 evidence 才配置 specialist |

這三段不是固定人數級距，也不會降低 evidence、authority、safety 或 review gate。Main 仍會提出具體完整 slate 與由角色推導出的各專業人數。使用者可以改 range 或角色；range 變更會重新計算整份 slate，並產生新的 digest-bound PlanRevision。

Actual-user coverage 與專業複雜度是兩個獨立維度。`lightweight` UI 任務仍可能需要兩種實質不同的使用者視角；反過來，`critical` backend 任務也不應硬加無關的使用者角色。

## 變更後 selector probes

Range 實作完成後，三個新的 fresh contexts 分別收到 neutral task brief 與目前的 skill runtime。每個 context 都只被要求產生初始角色提案並停在 role review；它們沒有收到預期 range、沒有執行任何 perspective，也沒有看到本報告。

| Probe | 建議 range | 專業席位 | 模擬 actual-user 席位 | 結果 |
| --- | --- | ---: | ---: | --- |
| CRM CSV 匯入 | `lightweight` | 1 位 Product Engineering generalist | 1 位 Workspace 管理員 | 沒有獨立 architecture、security 或 reliability 席 |
| 候補名單自動遞補 | `standard` | 3 位：容量／狀態、跨介面服務、通知恢復 | 3 位：客戶、第一線人員、CMS | 沒有自動加入 security 席；共享狀態與投遞 evidence 仍分開 |
| Identity／crypto／ledger migration | `critical` | 7 位 evidence-distinct specialists | 2 位：客戶、tenant 操作員 | 獨立覆蓋 identity、crypto、migration、accounting、legal/privacy、API 與 incident evidence |

三個提案都顯示 range 與理由、依具體 slate 推導席位數、區分 simulated-user 限制與專業 evidence，並等待後續由使用者發出的確認。觀察到的 2／6／9 席差異，符合角色粒度校準，而不是固定的 panel-size mapping。

這些 probes 是針對性行為證據，不能取代 repository 的完整 release scorecard。2026-08-28 scorecard 完成後，runtime 與 eval suite 都已變更；release 或全域安裝前，仍需要一份綁定目前 runtime 的 fresh full-suite 結果。

## GUI 階段結論

Meeting core 的品質價值具有條件：

- 當任務具有真正不同的使用者目標、共享狀態權威，或單一 planner 容易混淆的失敗後果時使用；
- 有界任務預設採 `lightweight`；
- 不把角色數量包裝成品質；
- 在 freeze 前顯示 main 建議的 range 與理由，並允許使用者調整；
- 會議開始前就公開 proposed slate 的結構性成本。

對大眾市場 GUI 而言，關鍵優勢不是「多個 AI 在同一房間辯論」，而是可控制的 meeting workflow：main 提出最小充分角色集合、使用者可以修正或匯入角色 prompt、精確 slate 被 freeze，而且 evidence 保持可追溯。中高階使用者可以直接使用同一個 skill core；GUI 應降低設定與 review 摩擦，而不是隱藏 calibration 決策。

## 限制

- 只評估三個任務與一個 model family。
- Judges 看到的是 plans，不是完成的 implementation 或 production 結果。
- Actual-user roles 是模擬視角，不能取代使用者研究。
- 分數接近量表上限，存在 ceiling effect。
- 沒有量測精確 token、latency 與金錢成本。
- 實驗支持「有條件的效益」與 complexity-range 修正，但不能建立普遍適用的 effect size。
