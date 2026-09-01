# Complex Enough GitHub Pages 與 DNS 發布計畫

本文件是尚未執行的發布 runbook。Repository 內只準備 `site/` 與手動觸發的 Pages workflow；在使用者明確確認前，不啟用 Pages、不執行 workflow、不修改網站 DNS。

## 目標架構

- Canonical host：`https://complexenough.com`
- 英文首頁：`/en/`
- 繁體中文首頁：`/zh-TW/`
- Privacy、Terms、Support、Brand 各自保留雙語固定路徑。
- 網站為純靜態檔案，沒有 publisher analytics、cookies、表單或第三方字型。
- GitHub Actions 從 `site/` 建立 Pages artifact；workflow 目前只允許 `workflow_dispatch`，不會因 push 自動部署。

## 人工發布順序

1. 確認 repository 已公開且公開前內容檢查通過。
2. 在 GitHub 個人或 Organization 的 **Settings → Pages** 驗證 `complexenough.com`。GitHub 會提供 `_github-pages-challenge-…` TXT 名稱與精確 token；不得自行猜測。
3. 保留 domain verification TXT，不要在驗證後刪除。
4. 在 repository **Settings → Pages** 選擇 **GitHub Actions** 作為來源。
5. 先在 Pages 設定加入 `complexenough.com` 自訂網域，再修改 DNS。
6. 在 Cloudflare 新增 apex A records，全部設為 **DNS only**：

   - `185.199.108.153`
   - `185.199.109.153`
   - `185.199.110.153`
   - `185.199.111.153`

7. 可一併新增 apex AAAA records，全部設為 **DNS only**：

   - `2606:50c0:8000::153`
   - `2606:50c0:8001::153`
   - `2606:50c0:8002::153`
   - `2606:50c0:8003::153`

8. 新增 `www` CNAME 至 `complex-enough.github.io`，設為 **DNS only**。目標不可包含 repository path。
9. 不新增 wildcard DNS。不得刪除或覆蓋既有 Google Workspace MX、SPF、DKIM 與 domain verification TXT。
10. 手動執行 `Build GitHub Pages artifact` workflow。
11. 等 GitHub 完成 DNS check 後啟用 **Enforce HTTPS**。
12. 驗證 apex 與 `www`、兩種語言、四種政策頁、404、sitemap、手機版與無 JavaScript fallback。
13. URL 實際可用後，才把 OpenAI internal readiness 狀態往 `ready_to_submit` 推進。

## 回復方式

- Website deployment 可在 GitHub Pages 設定停用；不影響 repository source。
- DNS 回復時只移除本 runbook 新增的 Pages A／AAAA／CNAME。保留郵件、DKIM、SPF、Google 驗證與 GitHub domain verification TXT。
- Custom Actions deployment 不需要 repository root 的 `CNAME` 檔案。

## 官方參考

- [Using custom workflows with GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Managing a custom domain for GitHub Pages](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
- [Verifying your custom domain for GitHub Pages](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages)
