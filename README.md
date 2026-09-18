<div align="center">

# 🦞 LobsterAI AutoCheckin

**LobsterAI 每日自动签到 · 短信验证码登录 · 桌面端提取 Token · 多账号 · 自动续期 · 青龙友好**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/dependencies-requests%20%7C%20playwright-blue)](.)
[![Platform](https://img.shields.io/badge/platform-青龙%20%7C%20本地%20%7C%20GitHub%20Actions-blue)](.)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Stars](https://img.shields.io/github/stars/L0NE-6/LobsterAI-AutoCheckin?style=social)](https://github.com/L0NE-6/LobsterAI-AutoCheckin)

[✨ 特性](#-特性) · [🔑 获取 Token](#-获取-token新手必看) · [🚀 快速开始](#-快速开始) · [⚙️ 环境变量](#️-环境变量) · [❓ FAQ](#-常见问题)

</div>

---

## 📖 简介

**LobsterAI AutoCheckin** 是一套用于 LobsterAI（网易有道）的每日积分自动化工具，包含 3 个独立脚本：

| 脚本 | 作用 |
| :--- | :--- |
| `lobsterai_checkin.py` | 🎯 多账号每日签到，slot → context → check_in → 复核，自动续期 + 推送 |
| `lobsterai_login.py` | 🔑 从 LobsterAI 桌面客户端一键提取 accessToken + refreshToken（免抓包） |
| `lobsterai_sms.py` | 📲 手机号 + 短信验证码登录，手动过滑块后自动获取 Token（免客户端） |

签到与桌面端提取仅需 **requests**；短信登录需 **Playwright**（`pip install playwright && playwright install chromium`）。

---

## ✨ 特性

- 🔐 **Token 自动续期** — AT 快过期时用 RT 自动刷新，续期结果缓存到本地 JSON，形成滚动续期
- 👥 **多账号** — 支持任意数量账号，环境变量换行分隔即可配置
- ✅ **幂等安全** — 已签到 / 活动未投放 / 未发放三种情况都不会误计
- 📋 **结果复核** — 签到后再拉一次 context，只有 claimedToday 确实变化才算成功
- 🔄 **版本自动获取** — 从官方更新接口拉当前客户端版本，失败自动兜底
- 📢 **微信推送** — 可选 PUSHPLUS_TOKEN，签到结果推送到微信
- 🎨 **美观日志** — 带图标与分区的执行日志，状态一目了然
- 🪶 **轻量依赖** — 签到仅需 `requests`，无其他第三方库

---

## 🔑 获取 Token（新手必看）

> 这是**唯一**需要你手动准备的东西，弄到它就大功告成。

### ✅ 方式一：桌面客户端一键提取（推荐）

本仓库自带 `lobsterai_login.py`，会自动从 LobsterAI 桌面客户端的本地数据库读取登录凭据，**零抓包、不联网、不上传**。

```bash
# 1. 先在电脑上安装并登录 LobsterAI 桌面客户端
# 2. 运行提取脚本
python lobsterai_login.py

# 3. 终端会打印出 UID、AT 有效期、以及可直接粘贴的环境变量值
```

Token 存储在（Windows）：

```text
%APPDATA%/LobsterAI/lobsterai.sqlite
```

数据库 `kv` 表中键名 `auth_tokens` 的值就是 JSON 格式的 accessToken + refreshToken。
脚本是二进制格式的 SQLite 文件解析，所以用记事本打开是乱码是正常的。

### 📲 方式二：静默输出（脚本调用 / 青龙直填）

```bash
python lobsterai_login.py --export
```

直接输出一行 `uid:AT:RT` 格式，复制粘贴到青龙环境变量即可。

### 📲 方式三：短信验证码登录（无需桌面客户端）

没有装 LobsterAI 桌面客户端？用 `lobsterai_sms.py`，
自动打开浏览器 → 填手机号 → 手动拖滑块过验证 → 输入收到的验证码 → 自动换 Token。

```bash
# 先安装 Playwright（首次需要）
pip install playwright && playwright install chromium

# 运行
python lobsterai_sms.py
python lobsterai_sms.py 138xxxxxxxx
```

浏览器会自动打开登录页并填好手机号，你只需要：
1. 拖动滑块完成人机验证
2. 等手机收到验证码后输入

脚本会自动提交登录、截获回调 code 并换取 `uid:AT:RT`。

---

## 🚀 快速开始

### 青龙面板

1. **上传脚本** — 把 `lobsterai_checkin.py` 上传到青龙
2. **设置变量** — 环境变量 → 新建：

| 变量名 | 值 |
| :--- | :--- |
| `LOBSTERAI_TOKEN` | `uid:AT:RT`（从 `lobsterai_login.py --export` 获取） |

3. **设置定时** — 定时任务 → 新建：

```
0 9 * * *  python lobsterai_checkin.py
```

### GitHub Actions（免服务器）

仓库已内置 GitHub Actions workflow（`.github/workflows/lobsterai.yml`），每天北京时间 9:00 自动运行。

1. **Fork 本仓库**（或使用自己的私有仓库）
2. **设置 Secrets** — Settings → Secrets and variables → Actions → New repository secret：

   | Secret 名 | 值 |
   | :--- | :--- |
   | `LOBSTERAI_TOKEN` | `uid:AT:RT`（从 lobsterai_login.py 获取） |
   | `PUSHPLUS_TOKEN` | 可选，推送用 |

3. **手动测试** — Actions → LobsterAI Daily → Run workflow

> ⚠️ **建议将仓库设为 Private**：Actions 运行时会将续期后的 token 缓存提交到仓库（`lb_refresh_tokens.json`），公开仓库会跳过此步骤以避免 RT 泄露。私有仓库则自动持久化，长期免维护。

### 本地运行

```bash
# 全部账号签到
python lobsterai_checkin.py

# 只跑指定 UID
python lobsterai_checkin.py --only 10001

# 强制指定客户端版本（版本过期时用）
python lobsterai_checkin.py --version 2026.9.10
```

---

## ⚙️ 环境变量

| 变量 | 必填 | 说明 |
| :--- | :--- | :--- |
| `LOBSTERAI_TOKEN` | ✅ | 每行一个账号，格式 `uid:AT:RT` |
| `PUSHPLUS_TOKEN` | 可选 | 填了则推送签到结果到微信 |

### 多账号格式

```
10001:eyJhbGciOiJIUzUxMiJ9.xxx:eyJhbGciOiJIUzUxMiJ9.yyy
10002:eyJhbGciOiJIUzUxMiJ9.aaa:eyJhbGciOiJIUzUxMiJ9.bbb
```

- AT = accessToken（JWT，约 30 天有效）
- RT = refreshToken（JWT，约 180 天有效）
- uid = 账号 UID（脚本会自动从 JWT 解析，填错也能用）

---

## 📦 Token 续期机制

- 脚本每次运行时检查 AT 的 JWT `exp`，距过期 < 7 天时自动用 RT 续期
- 续期成功后新 token 缓存到脚本目录 `lb_refresh_tokens.json`
- 下次运行自动使用缓存的新 token，形成滚动续期
- RT 本身约 180 天有效，每次续期会换发新 RT 并立即保存

---

## ❓ 常见问题

<details>
<summary><b>为什么记事本打开 lobsterai.sqlite 是乱码？</b></summary>

SQLite 是二进制数据库格式，不是纯文本。用 `lobsterai_login.py` 提取即可，脚本内部用 Python 的 `sqlite3` 模块解析。

</details>

<details>
<summary><b>AT 过期了怎么办？</b></summary>

如果配置了 RT（格式 `uid:AT:RT`），脚本会在 AT 距过期 < 7 天时自动续期，无需手动干预。只填了 AT 没填 RT 的，AT 过期后需重新运行 `lobsterai_login.py` 提取新的。

</details>

<details>
<summary><b>显示"上游未投放签到活动"怎么办？</b></summary>

可能是客户端版本过旧。运行时加 `--version 2026.9.10`（或更高版本）强制指定。脚本默认会自动获取最新版本，一般不需要手动填。

</details>

<details>
<summary><b>多账号怎么配置？</b></summary>

在电脑上打开 LobsterAI 桌面客户端，依次登录每个账号（切换登录），每次登录后运行一次 `lobsterai_login.py --export`，把得到的 `uid:AT:RT` 逐行追加到青龙环境变量的值里（换行分隔）。

</details>

---

## 📄 License

[MIT](LICENSE)
