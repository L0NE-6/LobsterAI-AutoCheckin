# 更新日志

## v1.1.0（2026-10-16）

- 文档补齐：新增 `CHANGELOG.md` 与 `requirements.txt`（签到 / 提取需 `requests`，短信登录可选 `playwright`）。
- README 新增「📁 目录结构」章节；「📌 版本与发布」补充更新记录入口。
- 仓库 topics 补齐（automation / checkin / python / qinglong 等）。
- 脚本代码零改动，升级不影响任何既有配置。

## v1.0.0（2026-10-04）

- 首个公开版本：LobsterAI 每日签到（多账号、Token 自动续期、PushPlus 微信推送、日志脱敏）。
- 幂等处理：已签到 / 活动未投放 / 未发放三种情况不误计，签到后回读 `claimedToday` 复核。
- 配套 `lobsterai_login.py`：桌面端登录态一键提取 / 静默导出环境变量。
- 配套 `lobsterai_sms.py`：手机号 + 短信验证码登录（Playwright，可选）。
- GitHub Actions 工作流（Fork 可用）与青龙面板部署说明。
