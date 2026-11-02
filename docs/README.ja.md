# 🦞 LobsterAI AutoCheckin

**LobsterAI のデイリーチェックインを自動化する、デスクトップ認証情報抽出・SMS ログイン・マルチアカウント・トークン更新対応ツールです。**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

> 完全な中国語ドキュメントは [../README.md](../README.md) にあります。

## 概要

LobsterAI AutoCheckin は、1 件または複数の LobsterAI アカウントで毎日の報酬を受け取ります。slot と context を読み取り、チェックインを送信し、その後に context を再取得して結果を確認します。実行結果は、取得成功、本日受取済み、上流で未提供、リクエスト失敗を区別します。

リポジトリには 3 つのスクリプトがあります。`lobsterai_checkin.py` はデイリーチェックイン、`lobsterai_login.py` はデスクトップクライアントからの認証情報抽出、`lobsterai_sms.py` は任意の Playwright ベース SMS ログインを担当します。チェックインとデスクトップ抽出には `requests` のみが必要で、Playwright は SMS ログイン専用です。

## 主な機能

- `slot → context → check_in → context` の順で実行します。
- `LOBSTERAI_TOKEN` により任意数のアカウントを扱えます。
- AT の有効期限まで 7 日未満になると RT で更新します。
- ローテーション後のトークンを `lb_refresh_tokens.json` に保存します。
- 受取済みとアクティビティ未提供を新しい報酬として扱いません。
- 公式更新 API からクライアントバージョンを取得し、手動指定にも対応します。
- PushPlus 通知を任意で送信し、通常ログでは認証情報をマスクします。

## 認証情報の準備

各アカウントは `uid:AT:RT` 形式です。AT のみでも実行できますが、期限切れ後は自動更新できません。

### デスクトップクライアントから抽出

LobsterAI デスクトップクライアントにログインした状態で実行します。

```bash
python lobsterai_login.py
python lobsterai_login.py --export
```

Windows では `%APPDATA%/LobsterAI/lobsterai.sqlite` を読み、`kv.auth_tokens` から `accessToken` と `refreshToken` を取得します。`--export` を付けると、そのまま使用できる `uid:AT:RT` の 1 行だけを出力します。

### SMS ログイン

```bash
pip install playwright
playwright install chromium
python lobsterai_sms.py
python lobsterai_sms.py 138xxxxxxxx
python lobsterai_sms.py --headless 138xxxxxxxx
```

画面の指示に従ってスライダーと SMS コードを完了すると、ログイン結果から `uid:AT:RT` を生成します。例の電話番号はコマンド形式の説明用です。

## 最小構成の Qinglong

1. `lobsterai_checkin.py` をアップロードします。
2. `pip3 install requests` で依存関係を導入します。
3. 環境変数を追加します。

```text
LOBSTERAI_TOKEN=UID_VALUE:AT_VALUE:RT_VALUE
```

4. 定期タスクのコマンドを設定します。

```bash
task lobsterai_checkin.py
```

推奨 cron:

```cron
0 9 * * *
```

複数アカウントは改行または `@` で区切ります。通知が必要な場合だけ `PUSHPLUS_TOKEN` を追加します。

## 最小構成の GitHub Actions

**Settings → Secrets and variables → Actions** に次の Secrets を追加します。

| Secret | 必須 | 用途 |
| :--- | :---: | :--- |
| `LOBSTERAI_TOKEN` | はい | 1 行以上の `uid:AT:RT` |
| `PUSHPLUS_TOKEN` | 任意 | PushPlus 通知トークン |

まず **Actions → LobsterAI Daily → Run workflow** を実行します。同梱のスケジュールは UTC `0 1 * * *`、北京時間の毎日 09:00 です。Fork 後にスケジュールワークフローが無効な場合は Actions 画面で有効化します。

`lb_refresh_tokens.json` をリポジトリへ保存するのは私有リポジトリだけです。公開リポジトリではローテーション後の RT を履歴へ残さないため、この保存処理をスキップします。公開リポジトリでは毎回有効な Secret が必要です。

## 主要な環境変数

| 変数 | 必須 | 説明 |
| :--- | :---: | :--- |
| `LOBSTERAI_TOKEN` | はい | `uid:AT:RT` 形式の複数アカウント認証情報 |
| `PUSHPLUS_TOKEN` | 任意 | 結果サマリーを送る PushPlus トークン |

## コマンドライン

| チェックインオプション | 動作 |
| :--- | :--- |
| なし | 全アカウントを実行 |
| `--only UID` | 指定 UID のみ実行 |
| `--version VERSION` | クライアントバージョンを強制指定 |
| `--auths PATH` | 環境変数がない場合にローカル auth ディレクトリを使う |
| `--base URL` | API ベース URL を上書き |

| ログインオプション | 動作 |
| :--- | :--- |
| `--export` | `uid:AT:RT` のみを出力 |
| `--manual` | 認証情報を手動で貼り付け |
| `--headless` | SMS ブラウザログインを非表示で実行 |

## 検証の考え方

チェックイン送信後にアカウント context を再取得します。HTTP 200 だけで成功とせず、更新後の `claimedToday` 状態で判定します。1 アカウントの失敗は残りのアカウント処理を止めません。`lb_refresh_tokens.json` は実際の認証情報を含むため、公開リポジトリへコミットしないでください。

## プライバシー

認証情報は環境変数、Secrets、またはローカルクライアントの保存領域からのみ読み取ります。データベース、AT/RT の出力、SMS コード、`lb_refresh_tokens.json`、未マスクのログを公開しないでください。Issue 添付前にアカウント識別子が残っていないか確認してください。

## リンク

- [Releases](https://github.com/L0NE-6/LobsterAI-AutoCheckin/releases)
- [Issues](https://github.com/L0NE-6/LobsterAI-AutoCheckin/issues)
- [中国語 README](../README.md)
- [変更履歴](../CHANGELOG.md)

## 免責事項

本プロジェクトは個人の学習と自動化を目的としています。LobsterAI、NetEase Youdao および関連サービスの利用規約を確認し、自己責任で使用してください。
