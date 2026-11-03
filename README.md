<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# 🦞 LobsterAI AutoCheckin

**LobsterAI 每日积分签到工具，支持桌面端凭据提取、短信登录、多账号、Token 续期与可选推送。**

[简体中文](README.md) · [English](docs/README.en.md) · [繁體中文](docs/README.zh-Hant.md) · [日本語](docs/README.ja.md) · [한국어](docs/README.ko.md) · [Português (BR)](docs/README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/LobsterAI-AutoCheckin?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/LobsterAI-AutoCheckin?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/%E9%9D%92%E9%BE%99-Qinglong-4EAA25?style=for-the-badge" />
<img src="https://img.shields.io/badge/GitHub%20Actions-Supported-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-F472B6?style=for-the-badge" />
<a href="https://github.com/L0NE-6/LobsterAI-AutoCheckin/releases"><img src="https://img.shields.io/badge/%E2%AC%87%20Download-Releases-2ea44f?style=for-the-badge&logo=github" /></a>

[✨ 30 秒速览](#-30-秒速览) · [🚀 青龙面板](#-青龙面板) · [☁️ GitHub Actions](#-github-actions) · [🔑 获取凭据](#-获取凭据) · [🔧 环境变量](#-环境变量) · [❓ 常见问题](#-常见问题) · [🚫 使用边界](#usage-policy) · [✦ 星轨](#-星轨-star-trail)

</div>

---

<a id="usage-policy"></a>
## 🚫 使用边界与转载声明

> [!IMPORTANT]
> **官方版本永久免费。** 未经作者书面许可，禁止付费包装、搬运引流、冒充作者，或使用作者身份与二维码制造官方授权假象。违规内容可能被要求下架；作者可暂停更新、归档或删除仓库及相关 Release。

本项目仓库、脚本、部署说明和 Release 下载始终免费公开。未经作者明确书面许可，禁止将本项目包装为付费资源、内部版、独家版、会员权益、收费课程、付费部署或包更新服务；禁止搬运到其他账号、群组、频道、网盘、电商或付费平台进行涨粉、截流、倒卖和引流；禁止删除作者与版权信息后冒充原创；禁止使用作者昵称、头像、二维码和项目名称制造官方授权假象。

> 如需商业合作、品牌授权、联合分发或使用作者名义提供付费服务，请先取得作者明确书面授权。完整规则、收款码防诈骗说明和违规处理方式见 **[NOTICE.md](NOTICE.md)**。

> 官方仓库和 Release 始终免费。第三方以“下载费 / 激活费 / 内部版 / 代部署 / 会员门槛”等名义收费，均与作者无关，请停止付款并保留证据。

> 对上述违规行为，作者有权要求立即停止传播、删除内容并下架相关商品或页面；并可视情况暂停更新、归档或删除本仓库及相关 Release、向平台投诉或采取进一步必要措施。

---

## ✨ 30 秒速览

| 维度 | 说明 |
| :--- | :--- |
| **用途** | 为 LobsterAI（网易有道）账号领取每日签到积分，并在签到后重新读取状态复核。 |
| **输入** | `LOBSTERAI_TOKEN`，每行一个 `uid:AT:RT`；可选 `PUSHPLUS_TOKEN`。 |
| **输出** | 分账号执行结果、成功 / 已签 / 未投放 / 异常统计、当日积分摘要与可选微信推送。 |
| **部署** | 青龙面板、GitHub Actions、Windows / Linux 本地运行。 |
| **依赖** | 签到与桌面端 Token 提取仅需 `requests`；短信验证码登录额外使用 Playwright。 |
| **成功判据** | 签到后重新读取 context，只有 `claimedToday` 状态确认后才按成功报告。 |

## ✨ 核心能力

- **每日签到**：按 `slot → context → check_in → context` 完成领取与复核。
- **多账号**：使用 `LOBSTERAI_TOKEN` 配置任意数量账号。
- **滚动续期**：AT 距过期不足 7 天时用 RT 刷新，并缓存轮换后的凭据。
- **三种取 Token 路径**：桌面 SQLite 提取、静默导出、Playwright 短信登录。
- **幂等处理**：已签到、活动未投放和未发放按不同状态说明。
- **版本探测**：从官方更新接口获取客户端版本，也可通过参数强制覆盖。
- **推送与脱敏**：可选 PushPlus 通知，日志不展示完整 Token。

## 🔑 获取凭据

签到脚本需要 `uid:AT:RT`。其中 AT 是 accessToken，RT 是 refreshToken；只提供 AT 也可以运行，但到期后需要重新登录。

### 方式一：读取桌面客户端

先在电脑上安装并登录 LobsterAI 桌面客户端，然后运行：

```bash
python lobsterai_login.py
```

工具默认扫描 Windows 下的：

```text
%APPDATA%/LobsterAI/lobsterai.sqlite
```

数据库 `kv` 表中的 `auth_tokens` 保存 `accessToken` 与 `refreshToken`。该文件是 SQLite 二进制数据库，直接打开可能出现乱码，应使用工具解析。

### 方式二：静默导出

```bash
python lobsterai_login.py --export
```

标准输出只有一行 `uid:AT:RT`，适合直接写入青龙环境变量。若无法读取桌面数据库，也可使用：

```bash
python lobsterai_login.py --manual
```

### 方式三：短信验证码登录

```bash
pip install playwright
playwright install chromium
python lobsterai_sms.py
python lobsterai_sms.py 138xxxxxxxx
python lobsterai_sms.py --headless 138xxxxxxxx
```

浏览器会打开登录页并填入手机号。按页面提示完成滑块、输入短信验证码后，脚本从回调中换取 `uid:AT:RT`。Playwright 仅用于这条可选登录路径。

> [!IMPORTANT]
> 不要把真实手机号、验证码、AT 或 RT 发到 Issue。示例中的手机号只用于说明命令位置。

## 🚀 青龙面板

1. 将 `lobsterai_checkin.py` 上传到青龙脚本目录。
2. 安装签到依赖：

   ```bash
   pip3 install requests
   ```

3. 添加环境变量：

   ```text
   LOBSTERAI_TOKEN=UID_VALUE:AT_VALUE:RT_VALUE
   ```

4. 新建定时任务，从脚本列表生成运行命令：

   ```bash
   task lobsterai_checkin.py
   ```

建议 cron：

```cron
0 9 * * *
```

青龙按面板本地时间解释 cron。多账号在 `LOBSTERAI_TOKEN` 中逐行追加，或使用脚本支持的 `@` 分隔。

## 🚀 GitHub Actions

仓库内置 [`.github/workflows/lobsterai.yml`](.github/workflows/lobsterai.yml)，定时为 UTC `0 1 * * *`，对应北京时间每天 09:00。

1. Fork 仓库，或导入到你自己的私有仓库。
2. 在 **Settings → Secrets and variables → Actions** 添加 Secrets。
3. 进入 **Actions → LobsterAI Daily → Run workflow** 手动验证。
4. 若 Fork 后定时 workflow 没有自动启用，在 Actions 页面手动启用。

| Secret | 必填 | 说明 |
| :--- | :---: | :--- |
| `LOBSTERAI_TOKEN` | ✅ | 一行或多行 `uid:AT:RT`。 |
| `PUSHPLUS_TOKEN` | ➖ | 可选 PushPlus 推送令牌。 |

工作流使用 `permissions: contents: write`，但只在**私有仓库**中持久化 `lb_refresh_tokens.json`。公开仓库会跳过硬编码提交，避免轮换后的 RT 泄露。公开仓库每次运行都应提供仍然有效的 Secret。

## 🔧 环境变量

| 变量 | 必填 | 说明 |
| :--- | :---: | :--- |
| `LOBSTERAI_TOKEN` | ✅ | 多账号签到凭据，格式 `uid:AT:RT`。 |
| `PUSHPLUS_TOKEN` | ➖ | 配置后把签到摘要推送到微信。 |

单账号示例：

```text
UID_VALUE:AT_VALUE:RT_VALUE
```

多账号示例：

```text
UID_1:AT_VALUE_1:RT_VALUE_1
UID_2:AT_VALUE_2:RT_VALUE_2
```

脚本也支持纯 AT、`uid:AT` 和以 `@` 分隔多个条目。只配置 AT 时不会自动续期。

## 🔁 Token 续期

- 每次运行检查 AT 的 JWT `exp`。
- AT 距过期不足 7 天时，使用 RT 请求续期。
- 续期成功后写入脚本目录的 `lb_refresh_tokens.json`。
- 下一轮优先读取缓存中的最新 AT / RT。
- 每次刷新可能轮换 RT，因此缓存文件同样属于敏感凭据。

在青龙或可写脚本目录中，缓存可以持续保留；在临时容器或 Public Actions 运行中，不要依赖缓存长期存在。

## ⌨️ 命令行参数

| 签到参数 | 作用 |
| :--- | :--- |
| （无） | 运行全部账号。 |
| `--only UID` | 只运行指定 UID。 |
| `--version VERSION` | 强制指定客户端版本。 |
| `--auths PATH` | 指定本地 `auths` 目录；环境变量为空时使用。 |
| `--base URL` | 覆盖上游 API 地址。 |

| 登录工具参数 | 作用 |
| :--- | :--- |
| `--export` | 只输出 `uid:AT:RT`。 |
| `--manual` | 手动粘贴 Token。 |
| `--headless` | 短信登录无头浏览器模式。 |

## 🧪 执行与复核语义

- 签到前读取 slot / context，识别当天是否已经完成。
- 活动未投放、账号未获得奖励和接口异常分别记录。
- 调用 `check_in` 后再次读取 context，用 `claimedToday` 的状态变化复核。
- 单个账号失败不会中断其余账号。
- 进程输出区分成功、已签、未投放和异常数量。

## 🗂️ 数据文件

| 文件 | 内容 | 是否提交 |
| :--- | :--- | :---: |
| `lb_refresh_tokens.json` | 续期后的轮换 Token | ❌ 已忽略；私有 Actions 会单独持久化 |
| `.lobsterai_token.json` | 可能的本地 Token 状态 | ❌ 已忽略 |
| `lobsterai-*.json` | 本地账号文件 | ❌ 已忽略 |
| `auths/` | 本地授权目录 | ❌ 已忽略 |
| `*.log` | 运行日志 | ❌ 已忽略 |

## 🔒 隐私说明

- 脚本不包含真实账号、手机号、AT 或 RT。
- 签到来自环境变量 / Secret；本地提取只读取本机客户端数据库。
- 日志对 Token 进行裁剪或遮罩，但调试输出仍可能暴露账号标识，提交前请人工检查。
- `lb_refresh_tokens.json`、登录导出值和验证码都属于敏感数据，不要上传到公开仓库或 Issue。

## ❓ 常见问题

<details>
<summary><b>SQLite 文件打开后是乱码</b></summary>

`lobsterai.sqlite` 是二进制数据库。请运行 `python lobsterai_login.py`，工具会通过 SQLite 接口读取 `kv.auth_tokens`。
</details>

<details>
<summary><b>AT 过期后如何处理</b></summary>

配置了有效 RT 时，脚本会在 AT 距过期不足 7 天时自动续期。只有 AT 的配置在过期后需要重新运行桌面提取或短信登录。
</details>

<details>
<summary><b>提示上游未投放签到活动</b></summary>

先确认客户端版本。脚本默认从官方更新接口获取版本，也可临时指定：

```bash
python lobsterai_checkin.py --version 2026.9.10
```

版本号应替换为当前有效的官方版本。
</details>

<details>
<summary><b>Actions 没有按 09:00 运行</b></summary>

检查 workflow 是否启用、默认分支是否包含该工作流、仓库是否长期无活动，以及是否误把北京时间直接填进 GitHub cron。GitHub 的 cron 使用 UTC。
</details>

<details>
<summary><b>公共仓库为什么没有持久化 Token</b></summary>

工作流只在私有仓库提交 `lb_refresh_tokens.json`。公开仓库跳过持久化，避免轮换后的 RT 被写入公开历史。
</details>

## 📦 版本与发布

- 当前发布版：`v1.1.1`（2026-11-04，文档发行版；脚本逻辑仍为 `v1.1.0`）。
- 版本采用 `v主.次.修` 语义化格式。
- 所有历史版本保留在 [Releases](https://github.com/L0NE-6/LobsterAI-AutoCheckin/releases)。
- 变更记录见 [CHANGELOG.md](CHANGELOG.md)。

## ⚠️ 免责声明

本项目用于个人学习与自动化实践。请遵守 LobsterAI、网易有道及相关服务条款，并自行承担账号使用风险。

## ☕ 支持与反馈

遇到问题、有功能建议或发现兼容性变化，请提交 [Issue](https://github.com/L0NE-6/LobsterAI-AutoCheckin/issues)，附上脱敏日志、复现步骤和运行环境；代码改进可通过 [Pull Request](https://github.com/L0NE-6/LobsterAI-AutoCheckin/pulls) 提交。

项目免费开源。如果它节省了你的时间，可以自愿扫码支持；Star、真实运行反馈和文档修正同样有价值。

| 支付宝（支持信用卡 / 花呗） | 微信支付 |
| :---: | :---: |
| <img src="assets/donate/alipay.jpg" width="280" alt="支付宝赞赏码" /> | <img src="assets/donate/wechat.png" width="280" alt="微信赞赏码" /> |

> ⚠️ 收款码仅用于向作者自愿赞赏。任何第三方以代下载、代部署、内部资源或会员群为由收费，均与作者无关，请停止付款并保留证据。

---

## ✦ 星轨 Star Trail

> 每一次 Star 都是一枚坐标，记录这只自动化龙虾从单次签到游向稳定日常的路线。

<a href="https://star-history.com/#L0NE-6/LobsterAI-AutoCheckin&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=L0NE-6/LobsterAI-AutoCheckin&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=L0NE-6/LobsterAI-AutoCheckin&type=Date&theme=light" />
    <img alt="LobsterAI AutoCheckin Star Trail" src="https://api.star-history.com/svg?repos=L0NE-6/LobsterAI-AutoCheckin&type=Date&theme=light" />
  </picture>
</a>

---

<div align="center">
  <a href="https://github.com/L0NE-6/LobsterAI-AutoCheckin/releases">Releases</a> ·
  <a href="https://github.com/L0NE-6/LobsterAI-AutoCheckin/issues">Issues</a> ·
  <a href="https://github.com/L0NE-6/LobsterAI-AutoCheckin">Star</a>
  <br />
  <sub>L0NE-6 · DAILY SIGNAL · 让每一次签到都有回读、有记录、有分寸</sub>
</div>
