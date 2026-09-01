# Complex Enough 品質成效摘要

- 證據日期：2026-08-31
- 摘要範圍：使用者任務與 UI/UX Plan 品質
- 證據性質：受控、盲評、模擬使用者的方向性結果

## 一句話結論

受控評估中觀察到的平均分數提升約為**相對 Control 增加 5.0%–12.5%**，依評估範圍而異：

- 較廣的六任務 selective plan-only 盲評為 `+0.222/5`，約相對提升 `5.0%`；
- 聚焦 3–4 人 compact panel 的三任務盲評為 `+0.514/5`，約相對提升 `12.5%`。

後者就是「最終調整方案平均高於 0.5 分」的來源。它證明 compact 配置在該三個技術型 plan／spec 任務上的效果；前者涵蓋更多不同使用面，因此是較保守、較適合概括目前產品效果的數字。兩組結果不能合併成一個新的平均值，也不是「任何任務都會提高 5%–12.5%」的保證。

## 為什麼先改善 Plan

Complex Enough 的主要使用情境，是 Agent 已被授權主導設計與後續自動化開發。此時 Plan 不是只供閱讀的中間文件，而會成為 Spec、實作拆分、程式碼、測試與 review 的共同輸入。上游若遺漏使用者後果、權威來源、狀態交接或恢復路徑，下游 Agent 很可能忠實地把同一假設具體化，造成更昂貴的返工。

因此「先改善 Plan，避免缺口向 Spec 與 Implementation 傳播」是合理且重要的產品機制。不過目前評估只直接量測 Plan／plan-spec 分數，尚未量測完成實作、缺陷率或返工成本；不能把 `5.0%–12.5%` 再乘上一個假設倍率，宣稱為已證明的下游提升。後續最有價值的補強，是以相同 brief 封存 Control／Treatment Plan，交由 fresh agents 各自完成 Spec 與 Implementation，再盲評需求偏差、缺陷、返工與驗收結果。

## 核心數字

| 證據 | Control | Treatment | 觀察差值 | 適當解讀 |
| --- | ---: | ---: | ---: | --- |
| 六任務 plan-only 盲評 | 4.465/5 | 4.688/5 | `+0.222/5` | +4.4 個滿量表百分點；約 +5.0% 相對 Control |
| 三任務 compact panel 盲評 | 4.125/5 | 4.639/5 | `+0.514/5` | +10.3 個滿量表百分點；約 +12.5% 相對 Control |
| 三任務 Compact 對 Large 直接盲評 | 4.424/5 | 4.771/5 | `+0.347/5` | +6.9 個滿量表百分點；約 +7.8% 相對 Large，驗證 compact 調整本身 |
| 單一任務 pilot | 4.104/5 | 4.708/5 | `+0.604/5` | +12.1 個滿量表百分點；約 +14.7% 相對 Control，僅為單案方向性訊號 |
| Current-runtime contract gate | — | 120/120 assertions | 100% 通過 | 證明本版遵守已定義行為，不是品質提升 100% |

六任務結果另包含 Treatment 在 `5/6` 任務分數較高、evaluator 偏好票為 `13/18`；compact 三任務則是 `3/3` 勝出、偏好 `9/9`。這些比例是任務勝率與偏好率，不能改寫成品質提升 `83%`、`72%` 或 `100%`。

## 哪些面向改善最多

六任務使用八個等權、1–5 分的評估維度。Treatment 相對 Control 的平均差值為：

| 維度 | 差值 |
| --- | ---: |
| 範圍簡潔／避免過度設計 | `+0.583` |
| 狀態與結果清晰度 | `+0.444` |
| 防止誤操作 | `+0.444` |
| 任務符合度 | `+0.250` |
| 恢復是否可執行 | `-0.194` |

負向的 recovery 結果促成目前 runtime 的 minimum recovery closure。它也說明整體平均正向不代表每個品質面向都已改善。

## 建議公開用語

> 在受控盲評中，Complex Enough 觀察到約 `5.0%–12.5%` 的相對平均規劃分數提升：較廣的六任務 selective plan-only 評估提高 `0.222/5`（約 `5.0%`），聚焦 compact panel 的三任務評估提高 `0.514/5`（約 `12.5%`）。這是模擬使用者、特定模型與規劃階段的方向性結果，不代表所有任務或實際導入成果的保證。

若版面只能容納一個百分比：

- 描述整體產品效果時，使用較保守的「**六任務評估觀察到約 5.0% 的相對平均分數提升**」；
- 明確描述 compact panel 調整時，可使用「**三任務評估觀察到約 12.5% 的相對平均分數提升**」。

不可只寫「品質提升 12.5%」而省略三任務、規劃分數、Control 與方向性限制。

## 計算方式

- 滿量表百分點：`0.222 ÷ 5 × 100 = 4.44`
- 相對 Control 提升：`0.222 ÷ 4.465 × 100 ≈ 4.97%`
- Compact 滿量表百分點：`0.514 ÷ 5 × 100 = 10.28`
- Compact 相對 Control 提升：`0.514 ÷ 4.125 × 100 ≈ 12.46%`
- Compact 相對 Large 提升：`0.347 ÷ 4.424 × 100 ≈ 7.84%`
- 單案 pilot 相對提升：`0.604 ÷ 4.104 × 100 ≈ 14.72%`

百分比由報告中四捨五入後的公開平均值計算，因此以一位小數呈現，不主張統計顯著性。

## 適用邊界

- 評的是 Plan，不是完成後的軟體品質、商業 KPI 或 production outcome。
- evaluator 是 fresh context 的模擬使用者，且專業角色、Main、Control 與 evaluator 來自同一 model family。
- Compact 三任務評的是較技術型的 plan／spec，沒有隔離目前「先改善使用者任務與 UI/UX Plan」的完整核心產品效果，因此定位為次要機制證據。
- 六任務分數本來就偏高，存在 ceiling effect；`+0.222` 應解讀為小幅、方向性提升。
- 單一操作者、低後果且可逆的任務曾出現 `-0.167`；selective routing 是成效主張的一部分。
- 六任務 review 有已揭露但不影響分數的 output-taxonomy variance，因此狀態是 `PASS_WITH_DISCLOSED_NONSCORING_VARIANCE`，不是無保留的 protocol pass。
- 尚未由真人使用者、不同模型家族、production telemetry 或實作後結果重複驗證。

## 來源

- [Meeting core Plan-only 六案盲評](meeting-core-plan-only-batch6.zh-TW.md)
- [Meeting core 3–4 人 compact panel 規劃品質評估](meeting-core-compact-panel-comparison.zh-TW.md)
- [Meeting core 後續控制實驗](meeting-core-follow-up-experiments.zh-TW.md)
- [Meeting core 使用者驗證 Plan Pilot](meeting-core-user-validated-plan-pilot.zh-TW.md)
- [Codex current scorecard](../../evals/results/codex-2026-08-31.json)
