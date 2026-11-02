# 🦞 LobsterAI AutoCheckin

**LobsterAI 每日積分簽到工具，支援桌面端憑據擷取、簡訊登入、多帳號、Token 續期與可選推送。**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

> 完整中文文件請見 [../README.md](../README.md)。

## 概覽

LobsterAI AutoCheckin 可以為一個或多個 LobsterAI 帳號領取每日積分。流程會先讀取 slot 與 context，提交簽到，再重新讀取 context 核對結果。報告會區分成功領取、今日已簽、上游未投放活動與請求異常。

倉庫包含三個腳本：`lobsterai_checkin.py` 負責每日簽到，`lobsterai_login.py` 從桌面客戶端讀取憑據，`lobsterai_sms.py` 提供可選的 Playwright 簡訊登入。每日簽到與桌面端擷取只需要 `requests`，Playwright 僅供簡訊登入工具使用。

## 核心能力

- 執行 `slot → context → check_in → context` 流程。
- 使用 `LOBSTERAI_TOKEN` 支援任意數量帳號。
- AT 距到期不足 7 天時自動用 RT 續期。
- 把輪換後的 Token 寫入 `lb_refresh_tokens.json`。
- 正確區分今日已簽與活動未投放。
- 從官方更新介面取得用戶端版本，也允許手動覆蓋。
- 可選 PushPlus 推送，正常日誌會遮罩憑據。

## 準備憑據

每個帳號格式為 `uid:AT:RT`。只有 AT 也能執行，但到期後無法自動續期。

### 桌面端擷取

安裝並登入 LobsterAI 桌面客戶端後執行：

```bash
python lobsterai_login.py
python lobsterai_login.py --export
```

Windows 上會讀取 `%APPDATA%/LobsterAI/lobsterai.sqlite`，從 `kv.auth_tokens` 取得 `accessToken` 與 `refreshToken`。加上 `--export` 時只輸出一行可直接使用的 `uid:AT:RT`。

### 簡訊登入

```bash
pip install playwright
playwright install chromium
python lobsterai_sms.py
python lobsterai_sms.py 138xxxxxxxx
python lobsterai_sms.py --headless 138xxxxxxxx
```

依頁面提示完成滑塊並輸入簡訊驗證碼，工具會換取 `uid:AT:RT`。範例手機號只用於命令格式，請勿公開真實登入資料。

## 最短青龍設定

1. 上傳 `lobsterai_checkin.py`。
2. 安裝簽到依賴：`pip3 install requests`。
3. 新增環境變數：

```text
LOBSTERAI_TOKEN=UID_VALUE:AT_VALUE:RT_VALUE
```

4. 建立定時任務：

```bash
task lobsterai_checkin.py
```

建議 cron：

```cron
0 9 * * *
```

多帳號以換行或 `@` 分隔。需要推送時再設定 `PUSHPLUS_TOKEN`。

## 最短 GitHub Actions 設定

在 **Settings → Secrets and variables → Actions** 新增：

| Secret | 必填 | 用途 |
| :--- | :---: | :--- |
| `LOBSTERAI_TOKEN` | 是 | 一行或多行 `uid:AT:RT` |
| `PUSHPLUS_TOKEN` | 否 | PushPlus 推送令牌 |

先執行 **Actions → LobsterAI Daily → Run workflow**。內建排程使用 UTC `0 1 * * *`，即北京時間每天 09:00。Fork 後若排程工作流程被停用，請在 Actions 頁面啟用。

只有在私有倉庫中，工作流程才會把 `lb_refresh_tokens.json` 提交回倉庫。公開倉庫會跳過，避免輪換後的 RT 進入公開歷史；公開倉庫每次執行都需要有效 Secret。

## 關鍵環境變數

| 變數 | 必填 | 說明 |
| :--- | :---: | :--- |
| `LOBSTERAI_TOKEN` | 是 | 多帳號憑據，格式 `uid:AT:RT` |
| `PUSHPLUS_TOKEN` | 否 | PushPlus token，用於推送結果摘要 |

## 命令列參數

| 簽到參數 | 作用 |
| :--- | :--- |
| 無 | 執行全部帳號 |
| `--only UID` | 只執行指定 UID |
| `--version VERSION` | 強制指定用戶端版本 |
| `--auths PATH` | 環境變數不存在時使用本機授權目錄 |
| `--base URL` | 覆蓋 API 基底網址 |

| 登入參數 | 作用 |
| :--- | :--- |
| `--export` | 只輸出 `uid:AT:RT` |
| `--manual` | 手動貼上憑據 |
| `--headless` | 無介面執行簡訊瀏覽器登入 |

## 驗證語義

提交簽到後，腳本會重新讀取帳號 context。成功判斷基於刷新後的 `claimedToday` 狀態，而不是只有 HTTP 200。單一帳號失敗不會中止其他帳號。`lb_refresh_tokens.json` 包含真實憑據，請勿提交到公開倉庫。

## 隱私提醒

帳號憑據只應透過環境變數、Secrets 或本機客戶端儲存提供。請勿公開資料庫、匯出的 AT/RT、簡訊驗證碼、`lb_refresh_tokens.json` 或未脫敏日誌。提交 Issue 前仍應人工檢查帳號識別資訊。

## 連結

- [Releases](https://github.com/L0NE-6/LobsterAI-AutoCheckin/releases)
- [Issues](https://github.com/L0NE-6/LobsterAI-AutoCheckin/issues)
- [簡體中文完整文件](../README.md)
- [更新記錄](../CHANGELOG.md)

## 免責聲明

本專案供個人學習與自動化使用。請遵守 LobsterAI、網易有道與相關服務條款，並自行承擔使用風險。
