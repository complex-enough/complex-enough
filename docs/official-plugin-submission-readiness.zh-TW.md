# Complex Enough：OpenAI 官方 Plugin 送審準備紀錄

## 決策

以 **Complex Enough** 作為公開 plugin 品牌，先送出目前已通過行為驗證的 skills-only plugin，再開始 GUI。GUI、MCP server、遠端資料、帳號系統及遙測均不屬於本次送審範圍。

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

未來 GUI 會讓使用者逐回合從公開理由、證據、衝突與後果中學習領域知識與決策原因，並在最終 Plan 定版前追問 Main，或要求下一回合臨時加入／拆分視角。這是使用者學習與理解，不是模型訓練或永久記憶；也是 roadmap，而非 1.1.0 listing claim。GUI 仍只顯示結構化 public deliberation，不顯示 hidden reasoning 或 raw private transcripts。角色 prompt 的後續訓練不列入目前 roadmap。

## 已確認的公開身分

- 申請類型：個人。
- 公開 publisher／developer 候選顯示名稱：`Huan Min Wei`。
- GitHub Organization 與 repository：`complex-enough/complex-enough`。
- 官網：`https://complexenough.com/en/`，另提供 `/zh-TW/`。
- 支援：`support@complexenough.com`，best effort，不保證回覆或解決時限。
- Availability：portal 可選的全部國家與地區。
- 公開品牌與 directory display name：`Complex Enough`。
- 品牌短句：`The right perspectives. No more.`。
- 穩定 skill／plugin identifier：`orchestrate-multi-perspective-panel`。
- 既有 invocation、安裝路徑、schema URN 與 `1.x` public contracts 不因公開名稱或 repository namespace 調整而更名。

`Huan Min Wei` 必須在送審前與 OpenAI Platform 已驗證個人身分的實際顯示字串逐字比對。如果平台顯示順序或拼法不同，manifest、listing、官網及政策必須一起調整後重新驗證。

## Repository 內已完成

- Repo 根目錄仍是唯一 canonical skill source。
- Deterministic packaging 產生 `.codex-plugin/plugin.json`、plugin-level `skills/`、listing images、本機 marketplace 與 submission ZIP。
- `brand/` 保存 canonical SVG，`packaging/assets/` 保存 128px composer icon 與 512px light/dark listing logo。
- `site/` 保存無第三方 script、cookie、publisher analytics 或外部字型的英文／繁體中文靜態網站。
- Privacy policy、terms of use 與 support 已由 draft 轉為可發布雙語內容。
- Repository 已公開，Pages source 已選擇 GitHub Actions。`v1.1.0` tag 已成功觸發 Pages 部署，另保留手動恢復入口。
- `complexenough.com` 已完成 Organization domain verification、GitHub Pages custom domain、apex／`www` DNS 與 Enforce HTTPS。英文／繁中首頁、privacy、terms、support 與 brand 共 11 條公開路徑均已用桌面與手機 Playwright 匿名驗證；HTTP、`www` 與舊 GitHub Pages URL 都會導向 canonical HTTPS host。
- 自訂網域與 DNS 的人工發布／回復順序已記錄於 [`github-pages-and-dns-plan.zh-TW.md`](github-pages-and-dns-plan.zh-TW.md)。
- Portal 所需的 5 個正向與 3 個負向案例草稿已準備。
- `CONTRIBUTING.md`、`SECURITY.md`、`CODE_OF_CONDUCT.md` 與 Apache-2.0 license 已存在。

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

Current-runtime Codex gate 是 26/26 cases、59 public turns、120/120 assertions，由三個 fresh blind graders一致通過。這些證據不取代送審時在最終 host、精確 public release bytes 上重跑的 5 positive／3 negative portal cases。

## 隱私與歷史資料

Repository 公開 publisher 使用個人姓名、品牌網域與 Organization namespace；不主動公開私人 Gmail 地址。Git 作者與 tagger 使用 `Huan Min Wei <support@complexenough.com>`。

部分早期歷史 eval artifact 含 `/home/sai` 本機絕對路徑。它不是密鑰或使用者資料，但 artifact 與 scorecard digest 綁定；直接改寫會破壞保存的實驗證據。因此公開版保留原始歷史證據並揭露此限制。新的 current-runtime artifacts 不依賴該本機路徑。

## 仍需人工／外部完成

1. 在 OpenAI Platform 完成或確認個人身分驗證，逐字確認 publisher 顯示名稱。
2. 選擇具有 `Apps Management: Write` 的 organization／project。
3. 在最終提交 host 與精確 bundle bytes 上，以 fresh chats 執行 5 positive／3 negative portal cases。
4. 逐項完成 portal listing、availability、release notes、policy attestations 與 guidelines review。
5. 使用者明確授權後才提交官方審查。

## `ready_to_submit` terminal condition

只有下列條件全部成立，`submission/listing.json` 才可從 `awaiting_publisher_inputs` 改為 `ready_to_submit`：

1. OpenAI verified individual identity 與所有公開 publisher 字串一致。
2. Public repository 與所有政策 URL 已上線，可匿名存取。
3. Plugin Creator、Skill Creator 與 `python3 scripts/validate_repo.py` 全部通過。
4. 精確 release bundle 通過 fresh-host 5 positive／3 negative 測試。
5. Public release bytes、tag／release 與 submission bundle digest 相符。
6. 使用者明確授權 portal submission。

## 官方參考

- [Build skills](https://developers.openai.com/plugins/build/skills)
- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [Submit plugins](https://developers.openai.com/plugins/deploy/submission)
- [Plugin guidelines](https://developers.openai.com/plugins/app-guidelines)
- [Optimize metadata](https://developers.openai.com/plugins/guides/optimize-metadata)
- [Security and privacy](https://developers.openai.com/plugins/guides/security-privacy)
