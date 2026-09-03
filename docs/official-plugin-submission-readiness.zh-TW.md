# Complex Enough：OpenAI 官方 Plugin 送審與發布紀錄

## 決策

以 **Complex Enough** 作為公開 plugin 品牌，先發布已通過行為驗證的 skills-only plugin，再開始 GUI。GUI、MCP server、遠端資料、帳號系統及遙測均不屬於本次發布範圍。

OpenAI 的官方路徑是將 skill 包成 skills-only plugin，經 Platform submission portal 審查後發布到 ChatGPT 與 Codex 共用的 plugin directory。Repository 公開、GitHub Pages、DNS、OpenAI portal 寫入及 submission 都是分開的外部 gate。

## 送審價值定位

- Directory category：`Developer Tools`。
- Short description：`Agent-led plan quality control`。

### 1. 適合情境與範圍

- 核心類別：偏自動化開發情境中的 agent-led planning quality control。
- 主要使用者狀態：使用者只有目標，或只有部分領域知識，並授權 Agent 主導設計；不要求使用者先列出所有缺少的利害關係人與專業視角。
- 高價值觸發條件：不同使用者承受不同後果，或存在 authority、evidence、state、human/system handoff、stale state、誤操作與 recovery 風險。
- 不適用邊界：單一操作者、低後果、成熟且局部可逆的工作應留在 ordinary session；Complex Enough 的 selective routing 會主動避免沒有邊際價值的會議。
- 責任模型：使用者是老闆，擁有目標、scope 與重大決策；Main 是受委任的會議主管，負責判斷 meeting value、找齊最小充分視角、主持證據衝突並整合 Plan。

### 2. 與一般直接設計的差異

一般直接設計會由同一 Agent 依單一 working perspective 補足未知內容，接著讓該 Plan 成為 Spec 與實作的上游輸入。Complex Enough 在這之前加入選擇性品質閘門：Main 自動建立缺少的 evidence-distinct lenses，使用者確認完整角色組合，各視角獨立執行，最後由 Main 依 authority 與 evidence 整合為一份可稽核 Plan。它不是固定 panel、投票工具或 implementation task dispatcher。

- 主要效益：在 Plan 變成 Spec 與程式碼前找出錯誤假設，避免同一缺口向後續自動化流程傳播。
- 完整主結果：六任務盲評全部保留，平均分數為 `+0.222/5`，約相對 Control 提升 `5.0%`；B1 是刻意納入的簡單、可逆負向適用性案例，其 `-0.167` 沒有排除。
- 情境分層：同批 B4–B6 的多方狀態、權威或實體交接案例平均 `+0.403/5`，約為 B2–B3 平均 `+0.146/5` 的 `2.8` 倍。這只描述 score-delta magnitude，不是「品質提高 2.8 倍」，也不取代完整六任務主結果。
- 獨立補充證據：另一組聚焦 compact 的三任務盲評為 `+0.514/5`，約相對提升 `12.5%`。
- 不可把任務勝率、assertion pass rate、描述性分層或推測的下游放大改寫為普遍品質提升百分比；目前尚未直接量測 Spec／Implementation outcome。

相鄰但不同的互動式需求引導，主要透過 Agent 反覆詢問使用者來完善需求。Complex Enough 的主要價值是當使用者只提供目標或部分領域知識、並希望 Agent 主導規劃時，自動補齊互相獨立的專業與實際使用視角，同時保留使用者的角色確認與重大決策權。

### 3. 後續延伸應用

Portal 與 reviewer talk track 應只承諾本次 skills-only 版本已具備的 selective routing、role proposal/review/freeze、independent perspectives、evidence adjudication 與 synthesis。

未來 GUI 會讓使用者逐回合從公開理由、證據、衝突與後果中學習領域知識與決策原因，並在最終 Plan 定版前追問 Main，或要求下一回合臨時加入／拆分視角。這是使用者學習與理解，不是模型訓練或永久記憶；也是 roadmap，而非 1.1.1 listing claim。GUI 仍只顯示結構化 public deliberation，不顯示 hidden reasoning 或 raw private transcripts。角色 prompt 的後續訓練不列入目前 roadmap。

## 已確認的公開身分

- 申請類型：個人。
- OpenAI Platform 已驗證的 publisher／developer 顯示名稱：`Huan Min Wei`。
- 送審 organization：`Personal`，portal 已接受其提交與發布權限。
- GitHub Organization 與 repository：`complex-enough/complex-enough`。
- 官網：`https://complexenough.com/en/`，另提供 `/zh-TW/`。
- 支援：`support@complexenough.com`，best effort，不保證回覆或解決時限。
- Availability：portal 可選的全部國家與地區。
- 公開品牌與 directory display name：`Complex Enough`。
- 品牌短句：`The right perspectives. No more.`。
- 穩定 skill、invocation 與本機 marketplace plugin identifier：`orchestrate-multi-perspective-panel`。
- OpenAI 官方 submission wrapper identifier：`complex-enough`。這只用來滿足 `plugin-name:skill-name` 合計不超過 64 字元的 portal ingestion 限制；ZIP 內的 skill 目錄與 `SKILL.md` 名稱仍是 `orchestrate-multi-perspective-panel`。
- 既有 invocation、安裝路徑、schema URN 與 `1.x` public contracts 不因官方 wrapper、公開名稱或 repository namespace 調整而更名。

`Huan Min Wei` 已在 portal 的 developer identity 選單與 OpenAI Platform 個人驗證結果完成逐字確認。

## Repository 內已完成

- Repo 根目錄仍是唯一 canonical skill source。
- Deterministic packaging 產生 `.codex-plugin/plugin.json`、plugin-level `skills/`、listing images、本機 marketplace 與 submission ZIP。
- Portal ingestion 實測發現 `plugin-name:skill-name` 合計 64 字元限制；1.1.1 打包流程保留原本本機 plugin／skill identifier，並只在官方 submission ZIP 產生 `complex-enough` wrapper manifest，組合長度由 71 降為 50。
- `brand/` 保存 canonical SVG，`packaging/assets/` 保存 128px composer icon 與 512px light/dark listing logo。
- `site/` 保存無第三方 script、cookie、publisher analytics 或外部字型的英文／繁體中文靜態網站。
- Privacy policy、terms of use 與 support 已由 draft 轉為可發布雙語內容。
- Repository 已公開，Pages source 已選擇 GitHub Actions。`v1.1.0` tag 已成功觸發 Pages 部署，另保留手動恢復入口。
- `complexenough.com` 已完成 Organization domain verification、GitHub Pages custom domain、apex／`www` DNS 與 Enforce HTTPS。英文／繁中首頁、privacy、terms、support 與 brand 共 11 條公開路徑均已用桌面與手機 Playwright 匿名驗證；HTTP、`www` 與舊 GitHub Pages URL 都會導向 canonical HTTPS host。
- 自訂網域與 DNS 的人工發布／回復順序已記錄於 [`github-pages-and-dns-plan.zh-TW.md`](github-pages-and-dns-plan.zh-TW.md)。
- Portal 所需的 5 個正向與 3 個負向案例草稿已準備。
- `CONTRIBUTING.md`、`SECURITY.md`、`CODE_OF_CONDUCT.md` 與 Apache-2.0 license 已存在。
- v1.1.1 skills-only submission 已通過 portal ingestion 與 Skills 檢查，狀態成為 `Approved`，並於 2026-09-03 由 publisher 執行 `Publish`。

產生送審包：

```bash
python3 scripts/package_plugin.py --replace
```

產物位於忽略追蹤的 `build/`，不提交第二份可能漂移的 runtime。

## 本機 smoke 與行為證據

機器可讀紀錄位於 [`submission/local-smoke-2026-08-31.json`](../submission/local-smoke-2026-08-31.json)，結果為 `pass_with_observations`：

- pure-function 負向案例直接回一般 session，沒有建立會議。
- lightweight CSV 案例提出兩個互補席位並停在 `awaiting_role_review`。
- 一次同名舊 personal skill 的來源碰撞已標為無效，同步 bytes 後才重跑。
- 一次通用 artifact review 證明 package discovery，但因缺少 artifact 且人工中止，不列為完成通過。

Current-runtime Codex gate 是 26/26 cases、59 public turns、120/120 assertions，由三個 fresh blind graders 一致通過。這些是產品行為證據；portal 的 ingestion、approval 與 publication 狀態另記錄於 [`submission/listing.json`](../submission/listing.json)。

## 隱私與歷史資料

Repository 公開 publisher 使用個人姓名、品牌網域與 Organization namespace；不主動公開私人 Gmail 地址。Git 作者與 tagger 使用 `Huan Min Wei <support@complexenough.com>`。

部分早期歷史 eval artifact 含 `/home/sai` 本機絕對路徑。它不是密鑰或使用者資料，但 artifact 與 scorecard digest 綁定；直接改寫會破壞保存的實驗證據。因此公開版保留原始歷史證據並揭露此限制。新的 current-runtime artifacts 不依賴該本機路徑。

## 發布結果

- 發布版本：`1.1.1`。
- 發布日期：2026-09-03。
- Portal 在提交後未出現可觀察的等待期即顯示 `Approved`；portal 沒有揭露採用的審查機制，因此本紀錄不再推論人工或自動審查。
- Publisher 隨後執行 `Publish`，完成 OpenAI universal Plugins Directory 發布。
- Portal 當時未提供可保存的穩定 listing permalink；目前以 Plugins Directory 搜尋 `Complex Enough` 作為公開定位方式。
- 後續版本仍須重新產生 deterministic ZIP、通過 repository validators，並以 portal 的更新流程提交；不得用已發布狀態略過新版驗證。

`submission/listing.json` 已由 `awaiting_publisher_inputs` 更新為 `published`，並保存 verified identity、organization、版本、日期、核准前狀態與 directory locator。這是目前發布狀態的 machine-readable source of truth。

## 官方參考

- [Build skills](https://developers.openai.com/plugins/build/skills)
- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [Submit plugins](https://developers.openai.com/plugins/deploy/submission)
- [Plugin guidelines](https://developers.openai.com/plugins/app-guidelines)
- [Optimize metadata](https://developers.openai.com/plugins/guides/optimize-metadata)
- [Security and privacy](https://developers.openai.com/plugins/guides/security-privacy)
