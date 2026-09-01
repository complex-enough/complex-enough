# Complex Enough 品質成效摘要

- 證據日期：2026-08-31
- 摘要範圍：使用者任務與 UI/UX Plan 品質
- 證據性質：受控、盲評、模擬使用者的方向性結果

## 一句話結論

主要公開結果採完整六任務 selective plan-only 盲評：Treatment 平均提高 `+0.222/5`，約相對 Control 提升 `5.0%`。六題全部保留，其中 B1 是刻意納入的簡單、單一操作者、低後果且可逆的負向適用性案例；其 `-0.167` 結果沒有被排除。

同一批次內，較符合產品目標情境的 B4–B6（多方狀態、權威或實體交接）平均提高 `+0.403/5`，相對其 Control 約提升 `9.2%`。其觀察差值約為 B2–B3 平均 `+0.146/5` 的 `2.8` 倍。這是保留全部資料後的描述性情境分層，不是刪除 B1 後重算整體效果，也不能改寫成「品質變成 2.8 倍」。

另一組獨立、聚焦 3–4 人 compact panel 的三任務盲評為 `+0.514/5`，約相對提升 `12.5%`。這就是「最終調整方案平均高於 0.5 分」的來源。它驗證 compact 配置在該三個技術型 plan／spec 任務上的效果，不能與六任務結果合併成新的平均值。

## 為什麼先改善 Plan

Complex Enough 的主要使用情境，是 Agent 已被授權主導設計與後續自動化開發。此時 Plan 不是只供閱讀的中間文件，而會成為 Spec、實作拆分、程式碼、測試與 review 的共同輸入。上游若遺漏使用者後果、權威來源、狀態交接或恢復路徑，下游 Agent 很可能忠實地把同一假設具體化，造成更昂貴的返工。

因此「先改善 Plan，避免缺口向 Spec 與 Implementation 傳播」是合理且重要的產品機制。不過目前評估只直接量測 Plan／plan-spec 分數，尚未量測完成實作、缺陷率或返工成本；不能把上述 planning uplift 再乘上一個假設倍率，宣稱為已證明的下游提升。後續最有價值的補強，是以相同 brief 封存 Control／Treatment Plan，交由 fresh agents 各自完成 Spec 與 Implementation，再盲評需求偏差、缺陷、返工與驗收結果。

## 核心數字

| 證據 | Control | Treatment | 觀察差值 | 適當解讀 |
| --- | ---: | ---: | ---: | --- |
| 六任務 plan-only 盲評 | 4.465/5 | 4.688/5 | `+0.222/5` | +4.4 個滿量表百分點；約 +5.0% 相對 Control |
| 六任務內 B4–B6 目標情境分層 | 4.375/5 | 4.778/5 | `+0.403/5` | 約 +9.2% 相對 Control；差值約為 B2–B3 的 2.8 倍，僅作描述性分層 |
| 三任務 compact panel 盲評 | 4.125/5 | 4.639/5 | `+0.514/5` | +10.3 個滿量表百分點；約 +12.5% 相對 Control |
| 三任務 Compact 對 Large 直接盲評 | 4.424/5 | 4.771/5 | `+0.347/5` | +6.9 個滿量表百分點；約 +7.8% 相對 Large，驗證 compact 調整本身 |
| 單一任務 pilot | 4.104/5 | 4.708/5 | `+0.604/5` | +12.1 個滿量表百分點；約 +14.7% 相對 Control，僅為單案方向性訊號 |
| Current-runtime contract gate | — | 120/120 assertions | 100% 通過 | 證明本版遵守已定義行為，不是品質提升 100% |

六任務結果另包含 Treatment 在 `5/6` 任務分數較高、evaluator 偏好票為 `13/18`；compact 三任務則是 `3/3` 勝出、偏好 `9/9`。這些比例是任務勝率與偏好率，不能改寫成品質提升 `83%`、`72%` 或 `100%`。

## 為什麼保留簡單任務

B1 在任務選擇時就被設計為檢查個人 dashboard 捷徑是否會被不必要地做成版面設計器。結果顯示一般 Plan 已足以處理這個成熟、可逆的單一操作者流程，而 Treatment 反而低 `-0.167`。這個結果支持 current runtime 的 selective routing：此類工作應回到 ordinary session，不應為了使用 skill 而開會。

嚴格來說，B1 是 **task-level negative-applicability case**，不是實驗 arm 的 `Control`；B1 到 B6 各自都有 Control 與 Treatment。保留這個術語差異，可以避免把「適用性邊界案例」誤寫成「被排除的異常值」。

B4–B6 的共同特徵也不是單純「任務比較大」，而是有多方承受不同後果、狀態或決定跨角色交接、權威來源分離，或錯用舊結果會產生營運／實體後果。`2.8` 倍描述的是這組案例相對 B2–B3 的**平均分數差值幅度**，不是整體品質倍數，也不是事前註冊的因果 subgroup estimate。

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

> 在完整六任務受控盲評中，Complex Enough 的平均規劃分數提高 `0.222/5`（約相對 Control 提升 `5.0%`）；資料保留一個結果為負的簡單、可逆負向適用性案例。同一批次內，多方狀態、權威或實體交接的 B4–B6 平均提高 `0.403/5`（約 `9.2%`），其分數差值約為 B2–B3 的 `2.8` 倍。這是描述性情境分層；另一組獨立的 compact-panel 三任務 benchmark 為 `+0.514/5`（約 `12.5%`）。所有數字都是模擬使用者、特定模型與規劃階段的方向性結果，不保證實際導入或下游實作品質。

若版面只能容納一個百分比：

- 描述整體產品效果時，使用較保守的「**六任務評估觀察到約 5.0% 的相對平均分數提升**」；
- 說明適用情境時，可使用「**B4–B6 的平均分數差值為 `+0.403/5`，約為 B2–B3 的 2.8 倍**」，並同時標示這是描述性分層而非品質倍數；
- 明確描述 compact panel 調整時，可使用「**三任務評估觀察到約 12.5% 的相對平均分數提升**」。

不可只寫「品質提升 12.5%」而省略三任務、規劃分數、Control 與方向性限制，也不可寫成「複雜任務品質提升 2.8 倍」。

## 計算方式

- 滿量表百分點：`0.222 ÷ 5 × 100 = 4.44`
- 相對 Control 提升：`0.222 ÷ 4.465 × 100 ≈ 4.97%`
- Compact 滿量表百分點：`0.514 ÷ 5 × 100 = 10.28`
- Compact 相對 Control 提升：`0.514 ÷ 4.125 × 100 ≈ 12.46%`
- Compact 相對 Large 提升：`0.347 ÷ 4.424 × 100 ≈ 7.84%`
- 單案 pilot 相對提升：`0.604 ÷ 4.104 × 100 ≈ 14.72%`
- B4–B6 Control：`(4.167 + 4.583 + 4.375) ÷ 3 = 4.375`
- B4–B6 Treatment：`(4.729 + 4.833 + 4.771) ÷ 3 ≈ 4.778`
- B4–B6 相對 Control：`0.403 ÷ 4.375 × 100 ≈ 9.21%`
- B4–B6 與 B2–B3 差值幅度比：`0.403 ÷ 0.146 ≈ 2.76`

百分比由報告中四捨五入後的公開平均值計算，因此以一位小數呈現，不主張統計顯著性。

## 適用邊界

- 評的是 Plan，不是完成後的軟體品質、商業 KPI 或 production outcome。
- evaluator 是 fresh context 的模擬使用者，且專業角色、Main、Control 與 evaluator 來自同一 model family。
- Compact 三任務評的是較技術型的 plan／spec，沒有隔離目前「先改善使用者任務與 UI/UX Plan」的完整核心產品效果，因此定位為次要機制證據。
- 六任務分數本來就偏高，存在 ceiling effect；`+0.222` 應解讀為小幅、方向性提升。
- 刻意納入的單一操作者、低後果且可逆負向適用性案例 B1 為 `-0.167`；它保留在六任務整體平均內，selective routing 是成效主張的一部分。
- B4–B6 與 B2–B3 的分層是描述性分析，未事前註冊為獨立因果 estimand；它支持產品適用性假設，但不取代完整六任務主結果。
- 六任務 review 有已揭露但不影響分數的 output-taxonomy variance，因此狀態是 `PASS_WITH_DISCLOSED_NONSCORING_VARIANCE`，不是無保留的 protocol pass。
- 尚未由真人使用者、不同模型家族、production telemetry 或實作後結果重複驗證。

## 來源

- [Meeting core Plan-only 六案盲評](meeting-core-plan-only-batch6.zh-TW.md)
- [Meeting core 3–4 人 compact panel 規劃品質評估](meeting-core-compact-panel-comparison.zh-TW.md)
- [Meeting core 後續控制實驗](meeting-core-follow-up-experiments.zh-TW.md)
- [Meeting core 使用者驗證 Plan Pilot](meeting-core-user-validated-plan-pilot.zh-TW.md)
- [Codex current scorecard](../../evals/results/codex-2026-08-31.json)
