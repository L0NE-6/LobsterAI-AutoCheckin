# 更新日志

## v1.1.1（2026-11-04）

- 文档发行版：同步首屏使用边界、反收费/反搬运声明、`NOTICE.md`、微信/支付宝赞赏码防诈骗提醒与六语导航。
- Release 完整包现在包含最新 README、NOTICE、docs 与图片资产；签到/领取主逻辑未变更，脚本版本仍为 `v1.1.0`。
- 验证：Markdown 渲染、相对链接、二维码资产与发布包清单检查通过；本版未使用真实账号执行签到。

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
