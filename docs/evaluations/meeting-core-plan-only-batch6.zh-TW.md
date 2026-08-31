# Meeting core Plan-only 六案盲評

- 評估日期：2026-08-31
- 評估範圍：上游使用者任務、UIUX Plan 品質與避免過度設計
- 不評：技術 Spec、API、架構、implementation 或安全工程
- Design revision：`planrev-core-plan-batch6-design-r2`
- Review revision：`planrev-core-plan-batch6-review-r1`
- Review digest：`sha256:fc031f1e3e0bcba4155e52455f2afa047d35be9c834a0b3c4ba832da7c84953e`
- 狀態：`BATCH_COMPLETED_WITH_NONSCORING_OUTPUT_VARIANCE`、`DIRECTIONAL_POSITIVE_WITH_BOUNDARY`

## 白話結論

這批結果支持繼續做 meeting core，但不支持「每個任務都開會」或「人越多越好」。

以每案的標準 Treatment 對一般 Agent Control 比較，六案中五案分數較高，18 位 fresh 模擬使用者 evaluator 中有 13 位偏好 Treatment。Treatment 平均 `4.688/5`，Control 為 `4.465/5`，差值 `+0.222`。這是穩定但不大的整體提升；真正有產品意義的是效果集中在預期位置：

- 範圍簡潔／避免過度設計：`+0.583`；
- 狀態與結果清晰度：`+0.444`；
- 防止誤操作：`+0.444`。

也有一個不能忽略的反例：Treatment 的「恢復是否可執行」平均比 Control 低 `-0.194`。多視角能刪掉多餘設計、釐清誰看到什麼與哪個結果有效，但 Main 壓縮 Plan 時，有時也把必要的 undo、返回修改、失敗重試或現場不一致後續一起壓掉。

結果顯示最重要的 routing 變數不是任務字面上的大小，而是：是否有兩個以上實際承受不同後果的人、是否存在決定／狀態交接，以及錯用舊結果是否會造成真實後果。

- 單一操作者、可逆、低後果的 B1，Treatment 反而低 `-0.167`。
- 有多方狀態、權威或實體交接的 B4、B5、B6，分別高 `+0.563`、`+0.250`、`+0.396`。
- B2、B3 只有小幅正效益，且不同 evaluator 的偏好不一致。

因此目前最合理的產品方向是：Main 先判斷是否值得開會及要幾個 evidence-distinct 使用者席位；使用者仍可調整。技術角色不預設加入這個上游 UIUX Plan 階段。進入 GUI 前，skill 應先把 selective routing 與最低 recovery closure 補進 runtime，再做 current-runtime behavioral release validation。

## 本批要回答的問題

相同原始任務與相近輸出格式下，先由 Main、領域專業及一至多位模擬 End user 建立 validated Plan，是否比一般 Agent 直接產生 Plan：

1. 更符合實際使用者任務與資訊需求；
2. 更清楚表達目前有效狀態、操作結果與交接；
3. 更不容易誤操作；
4. 更能避免單一 Agent 過度思考或加入不必要功能；
5. 同時仍足以交給普通 Agent 沿正常 Plan → Spec 流程繼續工作。

本批沒有執行 Spec 或 implementation。`Spec handoff` 只評 Plan 是否留下清楚邊界與待決事項，不評後續工程結果。

## 任務與實驗 arms

| 任務 | 實際使用面 | Treatment 主要問題 | Arms |
| --- | --- | --- | --- |
| B1 CMS 個人 dashboard 捷徑 | 高頻、偶爾與工作改變後的同一操作者 | 排序、隱藏、恢復與肌肉記憶，是否會被做成版面設計器 | Control；二席 Treatment |
| B2 CRM CSV 欄位 mapping 預覽 | 首次、模糊欄名與定期匯入 Admin | 是否在真正寫入前看懂來源欄去向、樣本限制及錯誤恢復 | Control；二席 Treatment |
| B3 公開內容勘誤 | 匿名讀者、需補充讀者、內容編輯 | reference、澄清、接受與實際修正是否被正確區分 | Control；三席 Treatment |
| B4 學校單日缺席申報 | 監護人、校務辦公室、教師 | 申請狀態、有效出勤結果、補件／修正與敏感資訊 | Control；標準三席；擴充四席 |
| B5 門市取貨替代品確認 | 顧客、低信心顧客、門市揀貨／交班 | 顧客接受、門市收到及目前可執行是否被拆開 | Control；三席 Treatment |
| B6 訪客登記變更 | Host、Guest、Front desk | 目前時間／地點／取消／check-in 邊界及舊資訊 | Control；標準三席；擴充四席 |

Main 是 moderator，不算 perspective seat。二席 Treatment 是一位領域專業加一位模擬 End user；三席／四席則依 evidence-distinct 使用面增加 End-user lens。

## 固定流程與成本

每個 Treatment arm 依相同順序執行：

1. 領域專業與 End user 在 fresh context 中各自 opening。
2. End user 在看到方案前先封存 unanchored task model。
3. 專業角色提出 10–16 個 bounded UI claims。
4. 同一 End user 只檢查 claims，不另做完整替代方案。
5. Main 只使用該 arm 的公開 evidence 綜合並封存 Plan。
6. 同案所有 Treatment 封存後，fresh Control 才只依原始 brief 產生一般 Plan。
7. Review round 的每位 evaluator 先做 Phase 1 task model，再依凍結順序閱讀匿名候選並評分。

兩候選任務使用 A→B、B→A、A→B；三候選任務使用 A→B→C、B→C→A、C→A→B。評審不知道來源 mapping、Design roles、其他評審結果、先前實驗或預期勝方。

- Design：46 perspective turns。
- Review：18 位 evaluator × 2 phases = 36 perspective turns。
- 合計：82 perspective turns。
- Retry、replacement、capacity degradation：皆無。

### 已揭露的 execution variance

Frozen Review plan 要求差距使用 `none／small／moderate／large`，並在每份 Phase 2 輸出明列 overdesign、shared gaps 與 confidence。實際派送的 Phase 2 指令改用 `small／material`，並要求最大優點、最大缺口、最小修正與限制；部分 evaluator 自行補了 shared gaps／confidence，部分沒有。

這是未經 revision 更新的輸出 taxonomy drift，不能標成完全 protocol pass。它沒有改變原始任務、角色、匿名順序、八個維度、1–5 分數、候選內容、來源遮蔽或偏好，因此本文保留數值與方向性結論，並把 gate 降為 `PASS_WITH_DISCLOSED_NONSCORING_VARIANCE`。若未來要比較 gap 等級分布，必須以新 revision 重跑；本報告不使用該 taxonomy 做聚合結論。

## Frozen Design roles

下列是實際生成候選 Plan 的完整 role identity。Main 負責 claims packet、authority／scope 裁決及 final synthesis，但不算獨立席位。

| 任務／arm | Role ID | Role revision | 類型與主要 lens |
| --- | --- | --- | --- |
| B1 Control | `role-b6-dashboard-baseline` | `rolerev-b6-dashboard-baseline-r1` | 一般 Agent，只依原始 brief 規劃 |
| B1 Treatment | `role-b6-dashboard-ux` | `rolerev-b6-dashboard-ux-r1` | 個人捷徑 UX、最小流程與 UI claims |
| B1 Treatment | `role-b6-dashboard-operator` | `rolerev-b6-dashboard-operator-r1` | 高頻 CMS 操作者的 opening 與 claim critique |
| B2 Control | `role-b6-csvmap-baseline` | `rolerev-b6-csvmap-baseline-r1` | 一般 Agent，只依原始 brief 規劃 |
| B2 Treatment | `role-b6-csvmap-ux` | `rolerev-b6-csvmap-ux-r1` | 欄位 mapping／preview UX 與 UI claims |
| B2 Treatment | `role-b6-csvmap-admin` | `rolerev-b6-csvmap-admin-r1` | Workspace Admin 的 mapping task model 與 critique |
| B3 Control | `role-b6-correction-baseline` | `rolerev-b6-correction-baseline-r1` | 一般 Agent，只依原始 brief 規劃 |
| B3 Treatment | `role-b6-correction-service` | `rolerev-b6-correction-service-r1` | 公開內容勘誤 service design |
| B3 Treatment | `role-b6-correction-reader` | `rolerev-b6-correction-reader-r1` | 匿名／公開讀者的送件與查詢後果 |
| B3 Treatment | `role-b6-correction-editor` | `rolerev-b6-correction-editor-r1` | 內容編輯的 triage、澄清與真實結案 |
| B4 expanded4 | `role-b6-absence-service` | `rolerev-b6-absence-service-r1` | 缺席申報 service design |
| B4 expanded4 | `role-b6-absence-guardian` | `rolerev-b6-absence-guardian-r1` | 監護人申報、補件與修正 |
| B4 expanded4 | `role-b6-absence-office` | `rolerev-b6-absence-office-r1` | 校務辦公室的版本與決定 |
| B4 expanded4 | `role-b6-absence-teacher` | `rolerev-b6-absence-teacher-r1` | 教師所需的唯一目前有效結果 |
| B4 standard3 | `role-b6-absence3-service` | `rolerev-b6-absence3-service-r1` | 缺席申報 service design |
| B4 standard3 | `role-b6-absence3-guardian` | `rolerev-b6-absence3-guardian-r1` | 監護人申報、補件與修正 |
| B4 standard3 | `role-b6-absence3-schoolstaff` | `rolerev-b6-absence3-schoolstaff-r1` | 校務辦公室＋教師的 composite school-staff lens |
| B4 Control | `role-b6-absence-baseline` | `rolerev-b6-absence-baseline-r1` | 一般 Agent，只依原始 brief 規劃 |
| B5 Control | `role-b6-substitution-baseline` | `rolerev-b6-substitution-baseline-r1` | 一般 Agent，只依原始 brief 規劃 |
| B5 Treatment | `role-b6-substitution-service` | `rolerev-b6-substitution-service-r1` | 單一替代提案 service design |
| B5 Treatment | `role-b6-substitution-customer` | `rolerev-b6-substitution-customer-r1` | 顧客比較、同意範圍與決定恢復 |
| B5 Treatment | `role-b6-substitution-picker` | `rolerev-b6-substitution-picker-r1` | 門市收件、可執行性與交班 |
| B6 expanded4 | `role-b6-visitor-service` | `rolerev-b6-visitor-service-r1` | 訪客登記變更 service design |
| B6 expanded4 | `role-b6-visitor-host` | `rolerev-b6-visitor-host-r1` | Host 修改／取消與結果確認 |
| B6 expanded4 | `role-b6-visitor-guest` | `rolerev-b6-visitor-guest-r1` | Guest 持舊資訊確認現況 |
| B6 expanded4 | `role-b6-visitor-frontdesk` | `rolerev-b6-visitor-frontdesk-r1` | Front desk 只採目前有效登記 |
| B6 standard3 | `role-b6-visitor3-service` | `rolerev-b6-visitor3-service-r1` | 訪客登記變更 service design |
| B6 standard3 | `role-b6-visitor3-hostguest` | `rolerev-b6-visitor3-hostguest-r1` | Host＋Guest composite lens |
| B6 standard3 | `role-b6-visitor3-frontdesk` | `rolerev-b6-visitor3-frontdesk-r1` | Front desk 目前有效結果與 check-in 邊界 |
| B6 Control | `role-b6-visitor-baseline` | `rolerev-b6-visitor-baseline-r1` | 一般 Agent，只依原始 brief 規劃 |

## 匿名候選與封存雜湊

| 任務 | 候選 | 字元 | SHA-256 | 解盲來源 |
| --- | --- | ---: | --- | --- |
| B1 | A | 1,887 | `d56d2d93da0401316823d4a1f716c9926f23f90e32da696d294f246822193707` | Control |
| B1 | B | 1,703 | `b886d4c04a745c0ef82e10d8d29ce35dcff6cc55bb35f710c0542f9d2aaefab2` | Treatment |
| B2 | A | 2,004 | `49951fc6873dd5dde81d3be62410e3c917fa70b31aac7fe7dfea1a40c7bce73b` | Control |
| B2 | B | 1,765 | `354989d862beb004468dd21909c68fb1624034b9b29a0513b7f5e34a1e383e60` | Treatment |
| B3 | A | 1,732 | `03c150c4478a2438a25982876a502af1d2254b099e696839a5d3361bead79a98` | Treatment |
| B3 | B | 1,950 | `dc40a64397faba3f68865ee8cbbe4fa5fcc74d168029c8ef3bbb1f02fdda7f84` | Control |
| B4 | A | 1,700 | `ac3aaea939c674e1186ccee357bbb87ed3c523d3b9fb907c33663e3677748211` | expanded4 Treatment |
| B4 | B | 1,944 | `fdb1dc3a7547d24cd8e87dd17178f160ef2d378fcb247bb08d86b619cc6bf1b9` | Control |
| B4 | C | 1,700 | `09581db6bfef6c620d2b52901dee7825285127f954db531802d4969fc1a9ac27` | standard3 Treatment |
| B5 | A | 1,704 | `04229c36cb12bf6c1c89c342c1462cd33f63c28b2d9efafe2a03455bbcdebb6f` | Treatment |
| B5 | B | 1,855 | `99123dd606ebd6fbc83df35d8cd8a9de5ea3c584126b525277aa20389ca0c3cf` | Control |
| B6 | A | 1,930 | `7d7ae030177a30155cfc9d740e9f782ee34069833a7110682f0d5446cbf4ae90` | expanded4 Treatment |
| B6 | B | 1,988 | `acc5af9a3d3a2c74efa1273b75dd982a8296b6281ae20cb9fcbee705f0288809` | Control |
| B6 | C | 1,960 | `dbcf5fec7ca546a8938cf5d71a6e2b2a177ea7724dea917f5d03679c398456cf` | standard3 Treatment |

每案最長／最短 arm 不超過 `1.15×`，且所有候選使用相同八節 Plan 格式，降低篇幅與版型混淆。

## Frozen Review roles

完整 EffectiveRole 由共同 review contract 與下列角色 entry 編譯而成。共同限制包括 fresh context、read-only、不得使用 subagent、不得看 mapping／peer findings，並只輸出公開 rationale。

| 任務 | Role ID／revision | 模擬情境 | 順序 | Role digest |
| --- | --- | --- | --- | --- |
| B1 | `role-b6-review-dashboard-frequent` / `rolerev-b6-review-dashboard-frequent-r1` | 每日固定順序使用少數 CMS 功能 | A→B | `sha256:333b7f95e600c098d1d502be3d5a51e342591339dcf3b2b6f102520fce280379` |
| B1 | `role-b6-review-dashboard-occasional` / `rolerev-b6-review-dashboard-occasional-r1` | 偶爾使用、低數位信心、容易中斷 | B→A | `sha256:96c69c6dcd2487045d972191421522666995589dfb015096c491a89ccff31fe4` |
| B1 | `role-b6-review-dashboard-rolechange` / `rolerev-b6-review-dashboard-rolechange-r1` | 工作改變後找回捷徑並重排 | A→B | `sha256:c98585ca3731686f3e22bd4e09f6252d5546cbba869ae46932f76f06f490d11a` |
| B2 | `role-b6-review-csvmap-firsttime` / `rolerev-b6-review-csvmap-firsttime-r1` | 首次匯入小型名單的 Admin | A→B | `sha256:ed292c5c493b8d28489b4ca0649d4c01aee7414ff652c6573cf087fffe092525` |
| B2 | `role-b6-review-csvmap-ambiguous` / `rolerev-b6-review-csvmap-ambiguous-r1` | 空白／重複 header、敏感樣本與含義不明 | B→A | `sha256:c9a453afc691d901f6e573010ed983fa54a13ec038757123a6db95fb491c599c` |
| B2 | `role-b6-review-csvmap-recurring` / `rolerev-b6-review-csvmap-recurring-r1` | 定期匯入、重視快速複核 | A→B | `sha256:f042967c8fd3edc1f704686c8a1b3c0cd28249a390dbede346c7286a0cdee91b` |
| B3 | `role-b6-review-correction-anonymous` / `rolerev-b6-review-correction-anonymous-r1` | 不登入且可能不留聯絡方式的讀者 | A→B | `sha256:b98098be36150c6ff10fba7b2700de1d9fb8f9f77503f32b343dfff79c629f25` |
| B3 | `role-b6-review-correction-clarify` / `rolerev-b6-review-correction-clarify-r1` | 被要求澄清並安全補充的讀者 | B→A | `sha256:049e201e3c83e0e883fc21a4ce8e6e89560aca5add467a11cace13249245ffe3` |
| B3 | `role-b6-review-correction-editor` / `rolerev-b6-review-correction-editor-r1` | 驗證、回覆且公開修正後才結案的編輯 | A→B | `sha256:d36f68ca45bfb5c6e0d2138df522619b5b16d42840990368554f5234311f947d` |
| B4 | `role-b6-review-absence-guardian` / `rolerev-b6-review-absence-guardian-r1` | 單日部分缺席、可能補件／修正的監護人 | A→B→C | `sha256:cdc06c57aca227eec7f4e163ed2bba0fab28f769682b680a43e726abd8ee0a10` |
| B4 | `role-b6-review-absence-office` / `rolerev-b6-review-absence-office-r1` | 處理待審、補件、重疊與更正的校務人員 | B→C→A | `sha256:8ea319680fefd02c915600ef4d6a741d2c82ce6f785fde530b3871add787e262` |
| B4 | `role-b6-review-absence-teacher` / `rolerev-b6-review-absence-teacher-r1` | 點名時只需目前有效結果的教師 | C→A→B | `sha256:41e826089b178bd8dddeece4ed86f7d0749d3cd7e3100e9c3f9869e6aaa3336d` |
| B5 | `role-b6-review-substitution-specific` / `rolerev-b6-review-substitution-specific-r1` | 對規格、成分／相容性及價量敏感的顧客 | A→B | `sha256:5635a5b16c08869a61d85936baaae8c2ef00ab2f1c9d815f9c5305d55b6fd441` |
| B5 | `role-b6-review-substitution-recovery` / `rolerev-b6-review-substitution-recovery-r1` | 接近期限、低信心、可能重按／用舊頁的顧客 | B→A | `sha256:188f79bdafb77f85f069a9f601c81d94a0941e76ada9f99b3a39d538570793de` |
| B5 | `role-b6-review-substitution-picker` / `rolerev-b6-review-substitution-picker-r1` | 交班後判斷目前是否可執行的揀貨員 | A→B | `sha256:6ab83ad7c695d2af3e7002f5a4a1f135032daf43d1aabb1e3e3c368dd967befd` |
| B6 | `role-b6-review-visitor-host` / `rolerev-b6-review-visitor-host-r1` | Guest 出發前修改／取消的 Host | A→B→C | `sha256:be60ac7b9add5fa81ae96142438c9bf64a811c39df5129bbb1ad62d85d7d8f64` |
| B6 | `role-b6-review-visitor-guest` / `rolerev-b6-review-visitor-guest-r1` | 持舊邀請／截圖出行的 Guest | B→C→A | `sha256:94d6f712ebc77778ea0b55b1d7e40fdff46831de68030459b598804220b041ae` |
| B6 | `role-b6-review-visitor-frontdesk` / `rolerev-b6-review-visitor-frontdesk-r1` | 久置頁、交班或並行操作下的 Front desk | C→A→B | `sha256:17b8019f53d837af1e63a257b2d8a5a919a1a79ce241ed8c40f4ac914817dd1a` |

## 評分方式

每位 evaluator 對每個匿名候選使用相同八個等權 1–5 分維度，可用 0.5 分：

1. 任務符合度；
2. 流程自然度；
3. 資訊出現時機；
4. 狀態與結果清晰度；
5. 防止誤操作；
6. 恢復是否可執行；
7. 範圍簡潔／避免過度設計；
8. 是否足以交給下一個 Agent 製作 Spec。

評審先獨立打分，再排名、判斷差距並提出最小必要修正。不得因技術欄位、API、架構、實作或資安細節加分或扣分。

## 主要結果：標準 Treatment 對 Control

B4、B6 的主要比較採 standard3 Treatment；expanded4 另在後節比較。

| 任務 | Control | 標準 Treatment | Treatment 差值 | 偏好票 |
| --- | ---: | ---: | ---: | --- |
| B1 dashboard shortcuts | 4.854 | 4.688 | -0.167 | Treatment 1；Control 2 |
| B2 CSV mapping | 4.188 | 4.333 | +0.146 | Treatment 1；Control 2 |
| B3 content correction | 4.625 | 4.771 | +0.146 | Treatment 2；Control 1 |
| B4 school absence | 4.167 | 4.729 | +0.563 | Treatment 3；Control 0 |
| B5 pickup substitution | 4.583 | 4.833 | +0.250 | Treatment 3；Control 0 |
| B6 visitor changes | 4.375 | 4.771 | +0.396 | Treatment 3；Control 0 |
| **六案／18 evaluator** | **4.465** | **4.688** | **+0.222** | **Treatment 13；Control 5** |

這是 18 份 evaluator score 的等權平均；因每案都是三位 evaluator，也同時等於六案 task mean 的等權平均。

### 八維平均

| 維度 | Control | 標準 Treatment | Treatment 差值 |
| --- | ---: | ---: | ---: |
| 任務符合度 | 4.528 | 4.778 | +0.250 |
| 流程自然度 | 4.500 | 4.583 | +0.083 |
| 資訊出現時機 | 4.500 | 4.639 | +0.139 |
| 狀態與結果清晰度 | 4.417 | 4.861 | +0.444 |
| 防止誤操作 | 4.389 | 4.833 | +0.444 |
| 恢復是否可執行 | 4.583 | 4.389 | **-0.194** |
| 範圍簡潔／避免過度設計 | 4.139 | 4.722 | **+0.583** |
| 後續 Spec handoff | 4.667 | 4.694 | +0.028 |

## 各 evaluator 結果

### B1、B2、B3、B5：兩候選

| 任務／evaluator | Control | Treatment | Treatment 差值 | 偏好 |
| --- | ---: | ---: | ---: | --- |
| B1 frequent | 4.813 | 4.875 | +0.063 | Treatment，small |
| B1 occasional | 4.938 | 4.563 | -0.375 | Control，small |
| B1 role-change | 4.813 | 4.625 | -0.188 | Control，small |
| B2 first-time | 4.563 | 4.375 | -0.188 | Control，small |
| B2 ambiguous | 3.563 | 4.375 | +0.813 | Treatment，material |
| B2 recurring | 4.438 | 4.250 | -0.188 | Control，small |
| B3 anonymous | 4.813 | 4.688 | -0.125 | Control，small |
| B3 clarify | 4.563 | 4.875 | +0.313 | Treatment，small |
| B3 editor | 4.500 | 4.750 | +0.250 | Treatment，small |
| B5 specific | 4.688 | 4.813 | +0.125 | Treatment，small |
| B5 recovery | 4.500 | 4.875 | +0.375 | Treatment，material |
| B5 picker | 4.563 | 4.813 | +0.250 | Treatment，small |

### B4、B6：三候選

| 任務／evaluator | Control | expanded4 | standard3 | 排名 |
| --- | ---: | ---: | ---: | --- |
| B4 guardian | 4.375 | 4.563 | 4.813 | standard3 > expanded4 > Control |
| B4 office | 4.250 | 4.375 | 4.750 | standard3 > expanded4 > Control |
| B4 teacher | 3.875 | 4.375 | 4.625 | standard3 > expanded4 > Control |
| **B4 平均** | **4.167** | **4.438** | **4.729** | **三人一致** |
| B6 host | 4.438 | 5.000 | 4.875 | expanded4 > standard3 > Control |
| B6 guest | 4.250 | 4.750 | 4.563 | expanded4 > standard3 > Control |
| B6 front desk | 4.438 | 4.938 | 4.875 | expanded4 > standard3 > Control |
| **B6 平均** | **4.375** | **4.896** | **4.771** | **三人一致** |

## 逐案解讀

### B1：良性負向案例

一般 Plan 已能用短流程處理排序、隱藏、取消、失敗與恢復。Treatment 更貼近固定位置與肌肉記憶，但在偶爾使用與工作改變情境漏掉較具體的 dirty state、完成後回復上一個人配置及全隱藏前提示。這證明 full meeting 不適合預設用於單一操作者、低後果且高度可逆的任務。

### B2：平均正向，但偏好票反向

Treatment 因 ambiguous-header evaluator 的 `+0.813` 大幅改善而在平均分勝出，但首次與定期 Admin 都小幅偏好 Control。Treatment 最有價值的內容是空白／重複 header 的位置辨認、遮罩權威，以及明說「前十筆不是全檔驗證」；代價是返回修改、重新選檔與恢復流程不如 Control 完整。這類任務不應只看平均分，應保留不同使用者 consequence 的分布。

### B3：小幅正向

Treatment 更清楚分開已收件、已接受、需要補充與公開內容真的已修正，也把澄清留在同一 reference 下。Control 對匿名聯絡方式、reference 保存與部分隱私提示更具體。這顯示多角色能改善狀態語意，但 Main synthesis 仍需保留匿名使用者的最低成功與恢復路徑。

### B4：標準三席最強

兩種 Treatment 都勝過 Control，但 standard3 比 expanded4 高 `+0.292`，三位 evaluator 排名完全一致。standard3 把校務辦公室與教師合成一個 school-staff lens，反而更清楚地保留「申請狀態不等於有效出勤結果」、教師只看唯一目前結果，以及 pending／補件不得冒充生效。expanded4 的更多獨立細節沒有在相同篇幅下轉成更好的 final Plan。

### B5：小型但有實體交接，穩定正向

三位 evaluator 都偏好 Treatment。主要改善是把「顧客決定已記錄」、「門市已接收」與「目前可執行」拆開，並限制接受只涵蓋畫面列明的替代品、規格、數量與價格。Control 的版本失效、舊頁與現場不一致處理更具體，因此 Treatment 仍需補完整的期限內變更閉環。這一案說明任務不必很大；只要決定會跨角色變成現場指令，meeting 就可能有價值。

### B6：四席有小幅額外價值

兩種 Treatment 都明顯勝過 Control；expanded4 又比 standard3 高 `+0.125`，三位 evaluator 排名一致。把 Host、Guest、Front desk 分開後，現場核對、舊邀請與最少揭露的恢復路徑略完整。standard3 已能清楚定義有效、取消、已 check-in 與無法確認，並以 `+0.396` 勝過 Control，所以額外一席帶來的是局部增益，不是基本可用性的前提。

## 三席與四席的結論

兩案呈現相反結果：B4 的 standard3 勝 expanded4；B6 的 expanded4 勝 standard3。六位 evaluator 對兩案的席位偏好正好 3–3，不能推論固定人數。

| 任務 | standard3 | expanded4 | expanded4 − standard3 | 解讀 |
| --- | ---: | ---: | ---: | --- |
| B4 school absence | 4.729 | 4.438 | -0.292 | Office＋Teacher 可合併；拆席後 final synthesis 反而較弱 |
| B6 visitor changes | 4.771 | 4.896 | +0.125 | Guest 舊資訊／揭露後果與 Host 不完全相同，拆席有小幅價值 |

這支持既有兩層模型：Main 直接產生多個專業／使用者 role，不增加 Department leader 層或複合權重。是否拆席應看 evidence、authority 與 failure consequence 是否真正不同，而不是按部門名稱或固定人數。

## 對核心產品假設的回答

### 有被支持的部分

- Skill 確實能把注意力從「還能加什麼功能」拉回「實際誰要完成什麼、現在什麼有效、出錯後怎麼辦」。
- 避免過度設計是本批最大平均改善，不只出現在大型任務。
- 狀態／結果與防誤操作是第二、第三大改善，符合 End user lens 的預期價值。
- 多角色／多交接任務比單人可逆任務更穩定受益。
- 技術角色不需要預設進入這個上游 Plan 會議；本批沒有因缺少技術席而無法比較使用者品質。

### 沒有被支持的部分

- 不能宣稱所有任務都改善；B1 是明確負向案例。
- 不能宣稱更多席位必然更好；B4 與 B6 的結果方向相反。
- 不能用平均分掩蓋 evaluator 分歧；B2 平均正向但兩人偏好 Control。
- 不能宣稱後續 Spec 或 implementation 品質已提高；本批未測該段。
- 不能把模擬 End user 當成人類研究、telemetry 或市場證據。

## 建議的 skill 修正

### 1. Main 先做適用性 routing

Main 產生角色 slate 前，先公開判斷：

- 是否有兩個以上 evidence-distinct 使用面；
- 是否有狀態、決定或責任交接；
- 錯用舊結果是否有真實營運／實體後果；
- 操作是否可逆、是否已有成熟簡單模式。

若是單一操作者、低後果、可逆且成熟的 UI pattern，優先 ordinary session 或 lightweight review；不需要為了使用 skill 而湊出會議。

### 2. 維持「Main＋專業＋End user」主流程，但 End user 數量動態化

最小有效核心仍是領域專業建立 bounded claims、End user 先 opening 再 critique、Main 負責 synthesis。需要幾位 End user 由 Main 依實際後果提出完整角色建議，使用者可直接接受或調整。B4 表明可合併的使用面應合併；B6 表明真正不同的 Guest consequence 可以拆席。

### 3. 加入最低 recovery closure，不增加技術席

每個實際使用者 lens 在 synthesis 前至少要關閉或明確標記：

- 送出／儲存結果不明；
- 返回修改或重選輸入；
- 舊頁、並行變更或版本失效；
- 已完成後的最小修正／撤回／人工接手方式；
- 無權決定時由哪個既有 authority 接手。

Main 的壓縮 pass 不得只保留 happy path。若 recovery 必須由既有政策決定，也要留下可見狀態、owner 與下一步，而不是整段刪除。

### 4. 不改成加權投票

本批的價值來自不同 consequence 被保留下來，不是 13–5 的票數本身。B2 正好說明單一少數角色可能指出影響很大的問題；Main 應依 evidence、authority、可逆性與後果裁決，而不是按席位或部門權重平均。

### 5. 進 GUI 前的最小驗證

本批已足以結束「是否值得繼續」的探索，不需要重跑先前所有 technical-plan 報告。下一步應：

1. 把 selective routing 與 recovery closure 寫入 runtime／contract 所需位置；
2. 加 deterministic compatibility 與 semantic tests；
3. 用 neutral fresh cases 驗證 B1 類任務會被降到 lightweight／ordinary path，B4–B6 類任務仍會選到 evidence-distinct users；
4. 完成 current-runtime Codex behavioral release scorecard；
5. 再進 GUI implementation。

## 證據邊界與限制

- 每個 arm 只生成一次，沒有估計生成隨機性或信賴區間。
- 專業、End user、Control 與 evaluator 都來自同一 model family；fresh context 能降低資訊污染，但不提供人類或模型多樣性。
- 模擬使用者不是訪談、可用性測試、field study、telemetry 或市場證據。
- Main 負責 Treatment synthesis，結果同時包含 moderator 品質。
- 分數普遍偏高，存在 ceiling effect；`+0.222` 應視為小幅方向性效果。
- B4、B6 的 seat-count 比較只有兩個任務，每個 arm 一次生成，不能估計固定最佳人數。
- 本批只比較 Plan；不能延伸宣稱技術正確性、工程成本、交付速度或 implementation 品質改善。
- 82 perspective turns 是 invocation count，不是 token、延遲或金錢成本；本批沒有量測後三者。

## Public evidence ledger

| Claim ID | 判定 | 公開證據與 locator | 來源 role revisions |
| --- | --- | --- | --- |
| `CLAIM-BATCH-PROTOCOL` | supported with disclosed variance | 本文「固定流程與成本」「已揭露的 execution variance」「Frozen Review roles」「Completion receipt」；18/18 evaluator 完成兩階段，但 Phase 2 gap/output taxonomy 漂移 | 全部 `rolerev-b6-review-*-r1` |
| `CLAIM-CORE-PLAN-DIRECTIONAL` | supported with boundary | 「主要結果」：六案 5 勝 1 負、13–5、平均 `+0.222` | 18 個 evaluator revisions |
| `CLAIM-OVERDESIGN-REDUCTION` | supported | 「八維平均」：scope concision `+0.583`，為最大提升 | 18 個 evaluator revisions |
| `CLAIM-STATE-MISOPERATION` | supported | 「八維平均」：狀態與防誤均 `+0.444` | 18 個 evaluator revisions |
| `CLAIM-UNIVERSAL-BENEFIT` | rejected | B1 Treatment `-0.167`，2/3 evaluator 偏好 Control | `rolerev-b6-review-dashboard-*-r1` |
| `CLAIM-RECOVERY-CLOSED` | rejected | recovery 平均 `-0.194`；B1、B2、B6 的 Treatment 均低於 Control | 對應 9 個 B1／B2／B6 evaluator revisions |
| `CLAIM-MORE-SEATS-BETTER` | rejected | B4 standard3 勝；B6 expanded4 勝；跨兩案偏好 3–3 | B4／B6 六個 evaluator revisions |
| `CLAIM-HANDOFF-PREDICTOR` | directionally supported | B4–B6 穩定正向；B1 負向；B2/B3 混合 | 18 個 evaluator revisions |
| `CLAIM-SPEC-IMPLEMENTATION` | not tested | 實驗明確排除後續 Spec／implementation | Review common protocol |

公開 evidence 只保留角色身分、候選雜湊、分數、可觀察 consequence、限制與 moderator synthesis；未持久化 raw subagent transcripts、private scratch 或 chain-of-thought。

## Completion receipt

- Design revision：`planrev-core-plan-batch6-design-r2`。
- Review revision：`planrev-core-plan-batch6-review-r1`。
- 使用者確認的 Review digest：`sha256:fc031f1e3e0bcba4155e52455f2afa047d35be9c834a0b3c4ba832da7c84953e`。
- Confirmation source：後續使用者回合明確確認；沒有同回合預派角色。
- Design candidates：6 個 Control、6 個標準 Treatment、B4／B6 各 1 個 expanded4 Treatment，全部封存後才開始 Review。
- Design execution：46/46 planned perspective turns completed。
- Review execution：18/18 planned evaluators、36/36 planned perspective turns completed。
- Fresh Phase 1 task models：18/18 completed before candidate access。
- Candidate orders：依凍結 A/B 與 A/B/C counterbalancing 執行。
- Retry／replacement／degradation：none。
- Missing planned roles：none。
- Protocol gate：`PASS_WITH_DISCLOSED_NONSCORING_VARIANCE`；不可宣稱 exact protocol pass。
- 核心 Plan 品質訊號：`DIRECTIONAL_POSITIVE_WITH_BOUNDARY`。
- GUI readiness：`PENDING_RUNTIME_ADJUSTMENT_AND_CURRENT_BEHAVIORAL_RELEASE`。
