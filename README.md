<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# 🦞 LobsterAI AutoCheckin

**LobsterAI 每日积分签到，支持桌面凭据提取、短信登录、多账号、Token 滚动续期与 context 回读。**

> 当前版本：**v1.1.2**（2026-11-24） · 核心能力：slot → context → check_in → context、桌面 SQLite、Playwright SMS

[简体中文](README.md) · [English](docs/README.en.md) · [繁體中文](docs/README.zh-Hant.md) · [日本語](docs/README.ja.md) · [한국어](docs/README.ko.md) · [Português (BR)](docs/README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/LobsterAI-AutoCheckin?style=for-the-badge&label=Release&color=2ea44f&logo=github" alt="Release" />
<img src="https://img.shields.io/github/stars/L0NE-6/LobsterAI-AutoCheckin?style=for-the-badge&label=Stars&color=FFC75F&logo=github" alt="Stars" />
<img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Qinglong-4EAA25?style=for-the-badge&logo=linux&logoColor=white" alt="Platform" />
<img src="https://img.shields.io/github/license/L0NE-6/LobsterAI-AutoCheckin?style=for-the-badge&label=License&color=F472B6" alt="License" />
<a href="https://github.com/L0NE-6/LobsterAI-AutoCheckin/releases"><img src="https://img.shields.io/badge/Download-Releases-2ea44f?style=for-the-badge&logo=github" alt="Download" /></a>

[🚫 使用边界](#usage-policy) · [✨ 30 秒速览](#overview) · [🧭 这是什么](#what-is-this) · [🔁 协议](#protocol) · [🔑 凭据](#credentials) · [🚀 本地](#local) · [🐧 青龙](#qinglong) · [☁️ Actions](#actions) · [⌨️ CLI](#cli-output) · [🧾 结果码](#result-codes) · [✅ 成功判据](#success) · [🧪 测试](#tests) · [🧱 设计原则](#design) · [🔒 隐私](#privacy) · [📁 目录](#layout) · [📦 版本](#release) · [⚠️ 免责声明](#disclaimer) · [☕ 赞赏](#donate) · [💬 反馈与 Star](#feedback)

</div>

---

<a id="usage-policy"></a>
## 🚫 使用边界与转载声明

> [!IMPORTANT]
> **官方版本永久免费。** 未经作者书面许可，禁止付费包装、搬运引流、冒充作者，或使用作者身份与二维码制造官方授权假象。

本项目仓库、脚本、部署说明和 Release 下载始终免费公开。未经作者明确书面许可，禁止将其包装为付费资源、内部版、独家版、会员权益、收费课程、付费部署或包更新服务；禁止搬运到其他账号、群组、频道、网盘、电商或付费平台进行涨粉、截流、倒卖和引流。

如需商业合作、品牌授权、联合分发或使用作者名义提供付费服务，请先取得作者明确书面授权。完整规则见 [NOTICE.md](NOTICE.md)。

---

<a id="overview"></a>
## ✨ 30 秒速览

| 维度 | 说明 |
| :--- | :--- |
| **做什么** | 为 LobsterAI 账号领取每日签到积分，并在签到后重新读取 context。 |
| **输入** | `LOBSTERAI_TOKEN`，每行一个 `uid:AT:RT`；可选 `PUSHPLUS_TOKEN`。 |
| **输出** | 分账号结果、成功/已签/未投放/异常统计、当日积分摘要和可选推送。 |
| **部署** | Windows、Linux、青龙面板、GitHub Actions。 |
| **依赖** | 签到与桌面提取仅需 `requests`；短信登录额外使用 Playwright。 |
| **成功判据** | 签到后 context 回读确认 `claimedToday` 状态变化。 |

---

<a id="what-is-this"></a>
## 🧭 这是什么

仓库包含三个工具：

- `lobsterai_checkin.py`：每日签到、Token 续期、结果复核。
- `lobsterai_login.py`：从桌面客户端 SQLite 提取凭据，或手动粘贴。
- `lobsterai_sms.py`：Playwright 短信验证码登录，可选。

签到脚本按 `slot → context → check_in → context` 执行。已签到、活动未投放、账号未获得奖励和接口异常分别记录，单账号失败不会中断其他账号。

---

<a id="protocol"></a>
## 🔁 协议、工作原理与回读

默认 API 基址为 `https://lobsterai-server.youdao.com`。

```text
GET  /api/client-activities/slot
GET  /api/client-activities/{code}/context
POST /api/client-activities/{code}/actions/check_in
GET  /api/client-activities/{code}/context
POST /api/auth/refresh
```

客户端版本默认 `2026.9.4`，可从官方更新接口读取新版本，也可通过 `--version` 强制指定。

Token 续期逻辑：

1. 解析 AT 的 JWT `exp`。
2. AT 距过期不足 7 天时，用 RT 请求 `/api/auth/refresh`。
3. 成功后写入 `lb_refresh_tokens.json`。
4. 下一轮优先使用缓存中的新 AT/RT。

签到动作完成后再次读取 context，只有 `claimedToday` 状态确认后才报告成功。

---

<a id="credentials"></a>
## 🔑 凭据与环境变量

| 变量 | 必填 | 说明 |
| :--- | :---: | :--- |
| `LOBSTERAI_TOKEN` | 是 | 多账号签到凭据，格式 `uid:AT:RT` |
| `PUSHPLUS_TOKEN` | 否 | PushPlus 推送 |

支持格式：

```text
UID:ACCESS_TOKEN:REFRESH_TOKEN
UID:ACCESS_TOKEN
ACCESS_TOKEN
```

多账号每行一条，也支持用 `@` 分隔。只提供 AT 时不会自动续期。

### 桌面客户端提取

```bash
python lobsterai_login.py
python lobsterai_login.py --export
python lobsterai_login.py --manual
```

默认读取 `%APPDATA%/LobsterAI/lobsterai.sqlite` 的 `kv.auth_tokens`。

### 短信登录

```bash
pip install playwright
playwright install chromium
python lobsterai_sms.py
python lobsterai_sms.py 138xxxxxxxx
python lobsterai_sms.py --headless 138xxxxxxxx
```

---

<a id="local"></a>
## 🚀 本地快速开始

```bash
python -m pip install -r requirements.txt
```

配置：

```text
LOBSTERAI_TOKEN=UID_VALUE:AT_VALUE:RT_VALUE
```

运行全部账号：

```bash
python lobsterai_checkin.py
```

只运行指定 UID：

```bash
python lobsterai_checkin.py --only UID_VALUE
```

---

<a id="qinglong"></a>
## 🐧 青龙面板

1. 上传 `lobsterai_checkin.py`。
2. 安装依赖：`pip3 install requests`。
3. 设置 `LOBSTERAI_TOKEN`。
4. 创建任务：

```text
0 9 * * * task lobsterai_checkin.py
```

青龙按面板本地时间解释 cron。脚本目录需要可写且可持久化，才能保留 `lb_refresh_tokens.json`。

---

<a id="actions"></a>
## ☁️ GitHub Actions

工作流位于 [`.github/workflows/lobsterai.yml`](.github/workflows/lobsterai.yml)，每天 UTC `0 1 * * *`（北京时间 09:00）运行，并支持手动触发。

| Secret | 必填 | 说明 |
| :--- | :---: | :--- |
| `LOBSTERAI_TOKEN` | 是 | 一行或多行 `uid:AT:RT` |
| `PUSHPLUS_TOKEN` | 否 | PushPlus |

未配置 `LOBSTERAI_TOKEN` 时，工作流输出中性跳过提示，不发送任何业务请求。工作流只在私有仓库持久化 `lb_refresh_tokens.json`；公开仓库跳过提交，避免轮换 RT 进入公开历史。

---

<a id="cli-output"></a>
## ⌨️ CLI 与输出

| 签到参数 | 作用 |
| :--- | :--- |
| 无 | 运行全部账号 |
| `--only UID` | 只运行指定 UID |
| `--version VERSION` | 强制指定客户端版本 |
| `--auths PATH` | 指定本地 auths 目录 |
| `--base URL` | 覆盖 API 地址 |

| 登录参数 | 作用 |
| :--- | :--- |
| `--export` | 只输出 `uid:AT:RT` |
| `--manual` | 手动粘贴 Token |
| `--headless` | SMS 登录无头模式 |

输出区分成功、已签、未投放和异常数量，并给出当日积分摘要。Token 在日志中裁剪或遮罩。

---

<a id="result-codes"></a>
## 🧾 结果码

| 结果 | 含义 |
| :--- | :--- |
| 成功 | `check_in` 后 context 回读确认 `claimedToday` 变化 |
| 已签 | 签到前 context 已显示今日完成 |
| 未投放 | `slotState` 不是 `available` 或没有活动 |
| 未发放 | 账号未获得本次奖励 |
| 异常 | 网络、鉴权、context 结构或响应异常 |
| 退出码 `0` | 正常完成，包括未配置凭据的中性跳过 |
| 退出码 `1` | 配置、登录、刷新或签到失败 |

---

<a id="success"></a>
## ✅ 成功判据

签到请求返回成功只是动作证据。脚本必须重新读取 context，并确认 `claimedToday` 或相关状态发生可验证变化。

签到前已经是今日完成时按幂等成功处理。活动未投放、账号未获得奖励和接口异常不能写成成功。

---

<a id="tests"></a>
## 🧪 测试

仓库当前没有独立 `tests/` 目录，发布前验证命令：

```bash
python -m py_compile lobsterai_checkin.py lobsterai_login.py lobsterai_sms.py
python lobsterai_checkin.py --help
python lobsterai_login.py --help
git diff --check
```

本节明确记录测试边界：以上检查验证语法、CLI 和文档改动，不替代真实账号的签到、续期与 context 回读。

---

<a id="design"></a>
## 🧱 设计原则

- **回读优先**：签到动作后必须重新读取 context。
- **滚动续期**：AT 临近过期时使用 RT 刷新并缓存。
- **账号隔离**：单个账号异常不中断其余账号。
- **最小依赖**：签到和桌面提取只依赖 `requests`。
- **凭据分级**：AT、RT、手机号和验证码都按密码级数据处理。
- **中性跳过**：Actions 未配置凭据时不发请求、不制造失败。

---

<a id="privacy"></a>
## 🔒 隐私与数据边界

| 文件 / 数据 | 内容 | 提交 |
| :--- | :--- | :---: |
| `lb_refresh_tokens.json` | 续期后的轮换 Token | 否 |
| `.lobsterai_token.json` | 本地 Token 状态 | 否 |
| `lobsterai-*.json` | 本地账号文件 | 否 |
| `auths/` | 本地授权目录 | 否 |
| `*.log` | 运行日志 | 否 |

日志可能包含账号标识，提交 Issue 前必须人工检查并脱敏。

---

<a id="layout"></a>
## 📁 目录结构

```text
LobsterAI-AutoCheckin/
├── .github/workflows/lobsterai.yml
├── assets/
│   ├── donate-wechat.png
│   └── donate-alipay.jpg
├── docs/
├── lobsterai_checkin.py
├── lobsterai_login.py
├── lobsterai_sms.py
├── CHANGELOG.md
├── LICENSE
├── NOTICE.md
├── requirements.txt
└── README.md
```

---

<a id="release"></a>
## 📦 版本与发布

- 当前版本：`v1.1.2`，修复 Actions 未配置凭据时固定退出 1 的问题。
- 历史版本保留在 [Releases](https://github.com/L0NE-6/LobsterAI-AutoCheckin/releases)。
- 变更记录见 [CHANGELOG.md](CHANGELOG.md)。

---

<a id="disclaimer"></a>
## ⚠️ 免责声明

本项目用于个人学习与合法自动化实践。使用者应自行遵守 LobsterAI、网易有道及相关服务条款，并承担误配置、凭据泄露或账号异常带来的风险。

---

<a id="donate"></a>
## ☕ 支持与投喂：微信与支付宝赞赏码

项目免费开源，赞赏纯自愿，不影响任何功能。

<p align="center">
  <img src="assets/donate-wechat.png" width="260" alt="微信赞赏码" />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/donate-alipay.jpg" width="260" alt="支付宝赞赏码" />
</p>

<p align="center"><sub>微信支付（左） · 支付宝（右）</sub></p>

> [!WARNING]
> 收款码仅用于向作者自愿赞赏。任何第三方以代下载、代部署、内部资源、会员群或官方授权为由收费，均与作者无关。

---

<a id="feedback"></a>
## 💬 反馈与贡献：Star History

遇到问题、有功能建议或发现兼容性变化，请提交 [Issue](https://github.com/L0NE-6/LobsterAI-AutoCheckin/issues)，附上脱敏日志、复现步骤和运行环境；代码改进可通过 [Pull Request](https://github.com/L0NE-6/LobsterAI-AutoCheckin/pulls) 提交。

<a href="https://star-history.com/#L0NE-6/LobsterAI-AutoCheckin&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=L0NE-6/LobsterAI-AutoCheckin&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=L0NE-6/LobsterAI-AutoCheckin&type=Date&theme=light" />
    <img alt="LobsterAI AutoCheckin Star History" src="https://api.star-history.com/svg?repos=L0NE-6/LobsterAI-AutoCheckin&type=Date&theme=light" />
  </picture>
</a>

<div align="center">

[⭐ Star](https://github.com/L0NE-6/LobsterAI-AutoCheckin) · [🍴 Fork](https://github.com/L0NE-6/LobsterAI-AutoCheckin/fork) · L0NE-6 · DAILY SIGNAL

</div>
