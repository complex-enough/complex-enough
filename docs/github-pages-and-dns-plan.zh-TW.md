# Complex Enough GitHub Pages 與 DNS 發布計畫

本文件是 GitHub Pages 與自訂網域發布 runbook。Repository 已公開，Pages source 已選擇 GitHub Actions；DNS 與官方送審仍是獨立的外部 gate。

## 目標架構

- Canonical host：`https://complexenough.com`
- 英文首頁：`/en/`
- 繁體中文首頁：`/zh-TW/`
- Privacy、Terms、Support、Brand 各自保留雙語固定路徑。
- 網站為純靜態檔案，沒有 publisher analytics、cookies、表單或第三方字型。
- GitHub Actions 從 `site/` 建立 Pages artifact。與 `packaging/plugin.json` 版本完全一致的 `v*` release tag 會自動部署；`workflow_dispatch` 保留為人工恢復方式。一般 branch push 不會發布網站。

## 發布順序

### Phase A：先發布預設 GitHub Pages 網址

1. 確認 repository 已公開且公開前內容檢查通過。
2. 在 repository **Settings → Pages** 選擇 **GitHub Actions** 作為來源。
3. 推送與 `packaging/plugin.json` 版本一致的 release tag，讓 `Publish GitHub Pages` workflow 自動部署。只有重跑或故障恢復時才使用 `workflow_dispatch`。
4. 驗證預設 `https://complex-enough.github.io/complex-enough/` 網址、兩種語言、四種政策頁、404、sitemap、手機版與無 JavaScript fallback。

### Phase B：取得 DNS 修改授權後切換自訂網域

5. 在 GitHub Organization 的 **Settings → Pages** 驗證 `complexenough.com`。GitHub 會提供 `_github-pages-challenge-…` TXT 名稱與精確 token；不得自行猜測。
6. 保留 domain verification TXT，不要在驗證後刪除。
7. 先在 repository Pages 設定加入 `complexenough.com` 自訂網域，再修改 DNS。
8. 在 Cloudflare 新增 apex A records，全部設為 **DNS only**：

   - `185.199.108.153`
   - `185.199.109.153`
   - `185.199.110.153`
   - `185.199.111.153`

9. 可一併新增 apex AAAA records，全部設為 **DNS only**：

   - `2606:50c0:8000::153`
   - `2606:50c0:8001::153`
   - `2606:50c0:8002::153`
   - `2606:50c0:8003::153`

10. 新增 `www` CNAME 至 `complex-enough.github.io`，設為 **DNS only**。目標不可包含 repository path。
11. 不新增 wildcard DNS。不得刪除或覆蓋既有 Google Workspace MX、SPF、DKIM 與 domain verification TXT。
12. 等 GitHub 完成 DNS check 後啟用 **Enforce HTTPS**。
13. 驗證 apex 與 `www`、兩種語言、四種政策頁、404、sitemap、手機版與無 JavaScript fallback。
14. URL 實際可用後，才把 OpenAI internal readiness 狀態往 `ready_to_submit` 推進。

## 回復方式

- Website deployment 可在 GitHub Pages 設定停用；不影響 repository source。
- DNS 回復時只移除本 runbook 新增的 Pages A／AAAA／CNAME。保留郵件、DKIM、SPF、Google 驗證與 GitHub domain verification TXT。
- Custom Actions deployment 不需要 repository root 的 `CNAME` 檔案。

## 官方參考

- [Using custom workflows with GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Managing a custom domain for GitHub Pages](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
- [Verifying your custom domain for GitHub Pages](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages)
