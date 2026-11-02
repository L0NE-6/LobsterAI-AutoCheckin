# 🦞 LobsterAI AutoCheckin

**Daily check-in for LobsterAI with desktop credential extraction, SMS login, multi-account support, token refresh, and optional notifications.**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

> Complete Chinese documentation: [../README.md](../README.md)

## Overview

LobsterAI AutoCheckin collects the daily LobsterAI reward for one or more accounts. The check-in flow reads the current slot and context, submits the check-in, then reads the context again to verify the result. A run distinguishes successful claims, accounts that were already checked in, activities not offered by the service, and request failures.

The repository contains three scripts: `lobsterai_checkin.py` for daily check-in, `lobsterai_login.py` for reading credentials from the desktop client, and `lobsterai_sms.py` for the optional Playwright-based SMS login flow. Daily check-in and desktop extraction require only `requests`; Playwright is needed only for the SMS login helper.

## Core capabilities

- Runs the `slot → context → check_in → context` check-in sequence.
- Supports any number of accounts through `LOBSTERAI_TOKEN`.
- Refreshes an AT with its RT when the access token is within seven days of expiry.
- Persists rotated tokens in `lb_refresh_tokens.json`.
- Handles already checked-in and unavailable-activity responses without treating them as new rewards.
- Resolves the current client version from the official update service, with an override option.
- Sends optional PushPlus notifications and masks credentials in normal logs.

## Credential preparation

Each account entry uses `uid:AT:RT`. An AT-only entry can run until it expires but cannot refresh automatically.

### Desktop extraction

Install and sign in to the LobsterAI desktop client, then run:

```bash
python lobsterai_login.py
python lobsterai_login.py --export
```

On Windows, the tool reads `%APPDATA%/LobsterAI/lobsterai.sqlite` and obtains `accessToken` and `refreshToken` from the `kv.auth_tokens` value. `--export` prints only the ready-to-use `uid:AT:RT` line.

### SMS login

```bash
pip install playwright
playwright install chromium
python lobsterai_sms.py
python lobsterai_sms.py 138xxxxxxxx
python lobsterai_sms.py --headless 138xxxxxxxx
```

Complete the slider if requested, enter the received SMS code, and the helper exchanges the login result for `uid:AT:RT`. Use a documentation-only phone number and never publish real login data.

## Minimum Qinglong setup

1. Upload `lobsterai_checkin.py`.
2. Install the sign-in dependency with `pip3 install requests`.
3. Add the environment variable:

```text
LOBSTERAI_TOKEN=UID_VALUE:AT_VALUE:RT_VALUE
```

4. Create a scheduled task with:

```bash
task lobsterai_checkin.py
```

Suggested cron:

```cron
0 9 * * *
```

For multiple accounts, separate entries with newlines or `@`. Add `PUSHPLUS_TOKEN` only when notification is wanted.

## Minimum GitHub Actions setup

Add these Secrets under **Settings → Secrets and variables → Actions**:

| Secret | Required | Purpose |
| :--- | :---: | :--- |
| `LOBSTERAI_TOKEN` | yes | One or more `uid:AT:RT` entries |
| `PUSHPLUS_TOKEN` | optional | PushPlus notification token |

Run **Actions → LobsterAI Daily → Run workflow** once. The included schedule uses UTC `0 1 * * *`, which is 09:00 Beijing time. If a fork has scheduled workflows disabled, enable the workflow from the Actions page.

The workflow persists `lb_refresh_tokens.json` only when the repository is private. Public repositories skip that commit so a rotated refresh token is not written to public history. Public users must keep a valid Secret available for each run.

## Key environment variables

| Variable | Required | Description |
| :--- | :---: | :--- |
| `LOBSTERAI_TOKEN` | yes | Multi-account credentials in `uid:AT:RT` format |
| `PUSHPLUS_TOKEN` | optional | PushPlus token for the result summary |

## Command-line options

| Check-in option | Effect |
| :--- | :--- |
| none | Run every account |
| `--only UID` | Run one UID |
| `--version VERSION` | Force a client version |
| `--auths PATH` | Use a local auth directory when the environment variable is absent |
| `--base URL` | Override the API base URL |

| Login option | Effect |
| :--- | :--- |
| `--export` | Print only `uid:AT:RT` |
| `--manual` | Paste credentials manually |
| `--headless` | Run the SMS browser login without a visible window |

## Verification semantics

The script reads the account context after submitting the check-in. Success is based on the refreshed `claimedToday` state, not on a bare HTTP 200. A failure for one account does not stop the remaining accounts. `lb_refresh_tokens.json` is credential material and must not be committed to a public repository.

## Privacy

Account credentials are supplied through environment variables, Secrets, or local client storage. Do not publish the database, exported AT/RT, SMS code, `lb_refresh_tokens.json`, or unredacted logs. Review debug output before attaching it to an Issue because account identifiers may still appear.

## Links

- [Releases](https://github.com/L0NE-6/LobsterAI-AutoCheckin/releases)
- [Issues](https://github.com/L0NE-6/LobsterAI-AutoCheckin/issues)
- [Chinese README](../README.md)
- [Changelog](../CHANGELOG.md)

## Disclaimer

This project is intended for personal learning and automation. Follow LobsterAI, NetEase Youdao, and related service terms. Use it at your own risk.
