#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 LobsterAI Daily Checkin - 独立签到脚本（青龙友好版）
════════════════════════════════════════════════════════════

📌 LobsterAI 每日签到（协议逆向自 LobsterAI 官方桌面客户端）
   流程：查 slot → 查 context → 提交 check_in → 复核结果

✨ 特性
   🔑 多账号      支持环境变量 + auths 目录双模式
   🔄 版本自动获取  从官方更新接口拉当前客户端版本（带 TTL 缓存），失败用兜底
   ✅ 幂等安全     已签到 / 活动未投放 / 未发放 三种情况都不会误计
   📋 结果复核     签到后再拉一次 context，只有 claimedToday 确实变化才算成功
   📢 推送通知     可选 PUSHPLUS_TOKEN，运行结果推送到微信
   🔐 Token 自动续期 AT 快过期时用 RT 自动刷新（离线续期，无需浏览器）
   🧩 青龙友好     支持环境变量 LOBSTERAI_TOKEN 直接填账号，无需 auths 目录

🚀 使用方法（青龙面板）
   1. 上传脚本     lobsterai_checkin.py
   2. 设置变量     LOBSTERAI_TOKEN（见下方格式说明）
   3. 定时任务     0 9 * * *    每天 9 点签到

🔑 获取 Token
   1. 电脑上安装并登录 LobsterAI 桌面客户端
   2. 运行 lobsterai_login.py 自动从桌面端提取 AT + RT
      （token 存储在 %APPDATA%/LobsterAI/lobsterai.sqlite → kv 表 → auth_tokens）
      python lobsterai_login.py           # 交互模式
      python lobsterai_login.py --export  # 直接输出 uid:AT:RT

🔑 环境变量格式（青龙变量 LOBSTERAI_TOKEN）
   每行一个账号，格式：uid:AT:RT
   AT = accessToken（JWT，约 30 天有效）
   RT = refreshToken（JWT，约 180 天有效）
   uid = 账号 UID（仅用于显示，脚本会自动从 JWT 解析）

   多个账号换行分隔（青龙变量框里直接换行写即可）：
      10001:eyJhbGciOiJIUzUxMiJ9.xxx:eyJhbGciOiJIUzUxMiJ9.yyy
      10002:eyJhbGciOiJIUzUxMiJ9.aaa:eyJhbGciOiJIUzUxMiJ9.bbb

   也可以只用 AT（不填 RT，AT 过期后需手动更新）：
      eyJhbGciOiJIUzUxMiJ9.xxx

   ⚠️ AT 和 RT 之间用英文冒号 : 分隔
   ⚠️ RT 是续期凭据，泄露了别人就能操作你的账号

📦 Token 续期机制
   · 脚本每次运行时检查 AT 的 JWT exp，距过期 < 7 天时自动用 RT 续期
   · 续期成功后新 token 缓存到脚本目录 lb_refresh_tokens.json
   · 下次运行自动使用缓存的新 token，形成滚动续期
   · RT 本身约 180 天有效，每次续期会换发新 RT 并立即保存

⚙️ 命令行参数
   python lobsterai_checkin.py               全流程
   python lobsterai_checkin.py --base <url>  覆盖上游地址
   python lobsterai_checkin.py --version <v> 强制指定客户端版本
   python lobsterai_checkin.py --only <uid>  只跑指定 UID
   python lobsterai_checkin.py --auths <dir> 指定 auths 目录（备用，无环境变量时使用）

📄 依赖：requests（pip3 install requests）
"""
import sys, os, json, time, uuid, base64, argparse, re
import requests

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ─────────────────── 配置 ───────────────────
DEFAULT_BASE = "https://lobsterai-server.youdao.com"
UPDATE_API_URL = "https://api-overmind.youdao.com/openapi/get/luna/hardware/lobsterai/prod/update"
DEFAULT_CLIENT_VERSION = "2026.9.4"
PLACEMENT_SLOT = "desktop_sidebar"
VERSION_OK_TTL = 6 * 3600
VERSION_FAIL_TTL = 10 * 60
REQUEST_TIMEOUT = 30
REFRESH_THRESHOLD = 7 * 86400  # AT 距过期 < 7 天时自动续期

# 本地续期缓存文件（与脚本同目录）
REFRESH_STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lb_refresh_tokens.json")

_version_cache = {"val": "", "at": 0, "failed": False}


def valid_version(v):
    return bool(re.match(r"^\d+(\.\d+)*$", v.strip()))


def fetch_latest_version():
    """从官方更新接口取当前线上客户端版本号。"""
    r = requests.get(UPDATE_API_URL, timeout=8, headers={"Accept": "application/json"})
    r.raise_for_status()
    d = r.json()
    v = str((d.get("data") or {}).get("value", {}).get("version", "")).strip()
    if not valid_version(v):
        raise ValueError("update api 返回异常版本 %r" % v)
    return v


def client_version(forced=""):
    """版本优先级：CLI --version > 缓存 > 官方接口 > 兜底常量。"""
    if forced and valid_version(forced):
        return forced
    now = time.time()
    ttl = VERSION_FAIL_TTL if _version_cache["failed"] else VERSION_OK_TTL
    if _version_cache["val"] and now - _version_cache["at"] < ttl:
        return _version_cache["val"]
    try:
        v = fetch_latest_version()
        _version_cache.update({"val": v, "at": now, "failed": False})
        return v
    except Exception:
        fb = _version_cache["val"] or DEFAULT_CLIENT_VERSION
        _version_cache.update({"val": fb, "at": now, "failed": True})
        return fb


# ─────────────────── JWT 工具 ───────────────────
def jwt_exp(token):
    """解码 JWT payload 的 exp（Unix 秒）；失败返回 0。"""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return 0
        payload = parts[1] + "=" * (4 - len(parts[1]) % 4)
        return int(json.loads(base64.urlsafe_b64decode(payload)).get("exp", 0))
    except Exception:
        return 0


def jwt_sub(token):
    """解码 JWT payload 的 sub（即 uid）。"""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return ""
        payload = parts[1] + "=" * (4 - len(parts[1]) % 4)
        return str(json.loads(base64.urlsafe_b64decode(payload)).get("sub", ""))
    except Exception:
        return ""


# ─────────────────── Token 续期 ───────────────────
def refresh_one(rt, base=DEFAULT_BASE):
    """用 refreshToken 换新的 accessToken + refreshToken，返回 (AT, RT) 或 (None, err)。"""
    now_ms = str(int(time.time() * 1000))
    body = {
        "refreshToken": rt,
        "firstKeyfrom": now_ms,
        "latestKeyfrom": now_ms,
        "version": "0.1.0",
        "uuid": str(uuid.uuid4()),
    }
    try:
        r = requests.post(base + "/api/auth/refresh", json=body, timeout=20,
                          headers={"Content-Type": "application/json", "Accept": "application/json",
                                   "User-Agent": "LobsterAI/" + client_version()})
        d = r.json()
        if d.get("code", -1) != 0:
            return None, "code=%d msg=%s" % (d.get("code"), str(d.get("msg", ""))[:100])
        data = d.get("data") or {}
        at = data.get("accessToken", "")
        nrt = data.get("refreshToken", "") or rt
        if not at:
            return None, "refresh_failed: no accessToken — re-login required"
        return at, nrt
    except Exception as e:
        return None, str(e)[:100]


def load_refresh_store():
    """读本地续期缓存 {uid: {access_token, refresh_token, updated}}。"""
    if os.path.exists(REFRESH_STORE):
        try:
            return json.load(open(REFRESH_STORE, encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_refresh_store(store):
    json.dump(store, open(REFRESH_STORE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def auto_refresh(accounts, base):
    """检查每个账号的 AT，快过期时用 RT 续期。原地更新 accounts 列表。"""
    store = load_refresh_store()
    changed = False
    for acc in accounts:
        uid = acc.get("uid", "")
        at = acc.get("token", "")
        rt = acc.get("rt", "")

        # 从缓存恢复上次续期的结果（缓存优先于环境变量/文件）
        cached = store.get(uid, {})
        if cached.get("access_token"):
            at = cached["access_token"]
        if cached.get("refresh_token"):
            rt = cached["refresh_token"]

        exp = jwt_exp(at)
        now = time.time()
        if exp > 0 and (exp - now) > REFRESH_THRESHOLD:
            # AT 还没快过期，直接用
            acc["token"] = at
            acc["rt"] = rt
            continue

        if not rt:
            if exp > 0:
                remaining_days = (exp - now) / 86400
                if remaining_days < 0:
                    print("⚠️ %s AT 已过期 %.1f 天且无 RT，需重新登录" % (uid, -remaining_days))
                else:
                    print("⚠️ %s AT 将在 %.1f 天后过期且无 RT，届时需手动更新" % (uid, remaining_days))
            acc["token"] = at
            continue

        # 需要续期
        print("🔄 %s AT 需续期（剩余 %.1f 天），用 RT 刷新..." % (uid, max(0, (exp - now) / 86400)))
        new_at, new_rt_or_err = refresh_one(rt, base)
        if new_at:
            acc["token"] = new_at
            acc["rt"] = new_rt_or_err
            store[uid] = {"access_token": new_at, "refresh_token": new_rt_or_err,
                          "updated": time.strftime("%Y-%m-%d %H:%M")}
            changed = True
            print("   ✅ 续期成功")
        else:
            print("   ❌ 续期失败: %s" % new_rt_or_err)
            acc["token"] = at
            acc["rt"] = rt

    if changed:
        save_refresh_store(store)
        print("📝 续期结果已缓存到 %s" % REFRESH_STORE)


# ─────────────────── 账号加载 ───────────────────
def parse_env_tokens(raw):
    """解析 LOBSTERAI_TOKEN 环境变量。
    每行格式：uid:AT:RT 或 AT（无 RT）
    分隔符支持换行或 @。
    """
    items = []
    if not raw:
        return items
    for line in raw.replace("@", "\n").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(":")
        if len(parts) >= 3 and not parts[0].startswith("eyJ"):
            # uid:AT:RT 格式
            uid = parts[0].strip()
            at = parts[1].strip()
            rt = ":".join(parts[2:]).strip() if len(parts) > 3 else parts[2].strip()
            if not uid:
                uid = jwt_sub(at)
            items.append({"uid": uid, "token": at, "rt": rt, "nickname": ""})
        elif len(parts) == 2 and not parts[0].startswith("eyJ"):
            # uid:AT 格式（无 RT）
            uid = parts[0].strip() or jwt_sub(parts[1].strip())
            items.append({"uid": uid, "token": parts[1].strip(), "rt": "", "nickname": ""})
        else:
            # 纯 AT（无 uid 前缀）
            if line.startswith("eyJ"):
                items.append({"uid": jwt_sub(line), "token": line, "rt": "", "nickname": ""})
    return items


def load_accounts(auth_dir, only_uid=None):
    """扫描 auths/ 下所有 lobsterai-*.json，解析出 accessToken + uid。"""
    if not os.path.isdir(auth_dir):
        return []
    accs = []
    for fname in sorted(os.listdir(auth_dir)):
        if not fname.startswith("lobsterai-") or not fname.endswith(".json"):
            continue
        path = os.path.join(auth_dir, fname)
        try:
            doc = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        auth = doc.get("auth") or doc
        account = doc.get("account") or {}
        token = auth.get("accessToken") or auth.get("access_token") or ""
        rt = auth.get("refreshToken") or auth.get("refresh_token") or ""
        uid = str(account.get("uid") or auth.get("uid") or "")
        nickname = account.get("nickname") or auth.get("nickname") or ""
        if not token:
            continue
        if only_uid and uid != only_uid:
            continue
        accs.append({"uid": uid, "token": token, "rt": rt, "nickname": nickname, "file": fname})
    return accs


def load_all_accounts(auth_dir, only_uid=None):
    """环境变量优先，无环境变量时回退到 auths 目录。"""
    env_raw = os.environ.get("LOBSTERAI_TOKEN", "").strip()
    if env_raw:
        accs = parse_env_tokens(env_raw)
        if only_uid:
            accs = [a for a in accs if a["uid"] == only_uid]
        if accs:
            return accs
    return load_accounts(auth_dir, only_uid)


# ─────────────────── 签到协议 ───────────────────
def new_session(token, base):
    s = requests.Session()
    s.headers.update({
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "LobsterAI/" + client_version(),
    })
    s.base = base.rstrip("/")
    return s


def _unwrap(resp):
    """解上游统一信封 {code, msg, data} → data。"""
    resp.raise_for_status()
    d = resp.json()
    if d.get("code", 0) != 0:
        raise RuntimeError("code=%d msg=%s" % (d.get("code"), d.get("msg", "")))
    return d.get("data") or {}


def api_get(s, path):
    r = s.get(s.base + path, timeout=REQUEST_TIMEOUT)
    return _unwrap(r)


def api_post(s, path, body):
    r = s.post(s.base + path, json=body, timeout=REQUEST_TIMEOUT)
    return _unwrap(r)


def activity_slot(s, ver):
    url = "/api/client-activities/slot?placement=%s&clientVersion=%s&containerApiVersion=2&platform=win32" % (
        PLACEMENT_SLOT, ver)
    return api_get(s, url)


def activity_context(s, code, rev):
    return api_get(s, "/api/client-activities/%s/context?configRevision=%d" % (code, rev))


def extract_credits(data):
    """从 action 响应里捞发放积分数（字段名上游多次改过，逐个试）。"""
    if not isinstance(data, dict):
        return 0
    for k in ("creditsGranted", "rewardCredits", "credits", "grantedCredits", "creditAmount"):
        v = data.get(k)
        try:
            f = float(v)
            if f > 0:
                return f
        except (TypeError, ValueError):
            pass
    return extract_credits(data.get("result"))


def do_checkin(s, log):
    """
    执行一次签到，返回 (status, message, credits_granted)
    status: ok | already | unavailable | error
    """
    ver = client_version()
    # 1) 查 slot
    slot = activity_slot(s, ver)
    activity = slot.get("activity")
    slot_state = slot.get("slotState", "")
    if not activity or slot_state != "available":
        msg = "上游未投放签到活动（slotState=%s, clientVersion=%s）。" % (slot_state, ver)
        msg += "若长期如此：尝试 --version 强制指定官方当前版本。"
        return "unavailable", msg, 0

    code = activity.get("activityCode", "")
    rev = activity.get("configRevision", 0)

    # 2) 查 context（是否今日已领、有哪些动作）
    ctx = activity_context(s, code, rev)
    if ctx.get("configRevision"):
        rev = ctx["configRevision"]
    state = ctx.get("state") or {}
    actions = ctx.get("actions") or []
    reward_credits = state.get("rewardCredits", 0)
    total_days = state.get("totalDays", 0)
    claimed_days = state.get("claimedDays", 0)
    streak = state.get("streakDays") or state.get("streak") or 0

    if state.get("claimedToday") or "check_in" not in [a.lower().strip() for a in actions]:
        if state.get("claimedToday") and streak > 0:
            return "already", "今天已签到（连登 %d 天）" % streak, 0
        return "already", "今天已签到", 0

    # 3) 执行签到
    body = {"configRevision": rev, "idempotencyKey": str(uuid.uuid4()), "payload": {}}
    resp = api_post(s, "/api/client-activities/%s/actions/check_in" % code, body)
    granted = extract_credits(resp)

    # 4) 复核：拉一次 context，确认 claimedToday / claimedDays 确实变化
    claimed = granted > 0
    try:
        after = activity_context(s, code, rev)
        after_state = after.get("state") or {}
        claimed = after_state.get("claimedToday", False) or after_state.get("claimedDays", 0) > claimed_days
        if after_state.get("claimedDays", 0) > 0:
            claimed_days = after_state["claimedDays"]
        new_streak = after_state.get("streakDays") or after_state.get("streak") or 0
        if new_streak > 0:
            streak = new_streak
    except Exception:
        pass

    if not claimed:
        return "already", "本次未发放（今日已领过）", 0

    if claimed_days == 0:
        claimed_days = (state.get("claimedDays", 0)) + 1
    remaining = total_days - claimed_days if total_days > 0 else 0

    if granted > 0:
        msg = "签到成功 +%g 分" % granted
    else:
        msg = "签到成功"
    if streak > 0:
        msg += "（连登 %d 天）" % streak
    if remaining > 0:
        msg += "，剩余 %d 天" % remaining
    return "ok", msg, granted


# ─────────────────── 单账号 ───────────────────
def run_account(idx, acc, base):
    uid = acc["uid"]
    nick = acc.get("nickname", "")
    tag = "账号%d[%s]" % (idx, uid or "?")
    lines = []

    def log(m):
        ts = time.strftime("%H:%M:%S")
        line = "[%s][%s] %s" % (ts, tag, m)
        print(line)
        lines.append(line)

    log("╭─ 👤 %s（%s）" % (nick or "账号", uid or "无UID"))
    if not acc.get("token"):
        log("  ❌ Token 为空，跳过")
        return {"idx": idx, "uid": uid, "status": "error", "msg": "Token 为空", "lines": lines}

    s = new_session(acc["token"], base)
    try:
        status, msg, granted = do_checkin(s, log)
    except Exception as e:
        status, msg, granted = "error", "异常: %s" % str(e)[:120], 0

    icon = {"ok": "✅", "already": "☑️", "unavailable": "🚫", "error": "❌"}.get(status, "❓")
    log("  %s %s" % (icon, msg))
    if granted > 0:
        log("  💰 本次获得: %g 分" % granted)
    log("╰─ 状态: %s" % status)
    return {"idx": idx, "uid": uid, "status": status, "msg": msg, "granted": granted, "lines": lines}


# ─────────────────── 推送 ───────────────────
def send_notify(title, content):
    token = os.environ.get("PUSHPLUS_TOKEN", "").strip()
    if not token:
        return False
    if len(content) > 18000:
        content = content[:18000] + "\n...(内容过长已截断)"
    try:
        r = requests.post("https://www.pushplus.plus/send",
                          json={"token": token, "title": title, "content": content, "template": "txt"},
                          timeout=20)
        d = r.json()
        if d.get("code") == 200:
            print("📢 推送成功")
            return True
        print("📢 推送失败: %s" % str(d.get("msg", ""))[:80])
    except Exception as e:
        print("📢 推送异常: %s" % str(e)[:80])
    return False


def build_summary(results):
    lines = ["🦞 LobsterAI 签到报告", ""]
    ok_n = sum(1 for r in results if r["status"] == "ok")
    already_n = sum(1 for r in results if r["status"] == "already")
    unavail_n = sum(1 for r in results if r["status"] == "unavailable")
    err_n = sum(1 for r in results if r["status"] == "error")
    total_granted = sum(r.get("granted", 0) for r in results)

    for r in results:
        icon = {"ok": "✅", "already": "☑️", "unavailable": "🚫", "error": "❌"}.get(r["status"], "❓")
        lines.append("%s 账号%d [%s] %s" % (icon, r["idx"], r["uid"], r["msg"]))

    lines.append("")
    lines.append("📊 成功 %d | 已签 %d | 未投放 %d | 异常 %d" % (ok_n, already_n, unavail_n, err_n))
    if total_granted > 0:
        lines.append("💰 合计获得: %g 分" % total_granted)
    lines.append("🕐 %s" % time.strftime("%Y-%m-%d %H:%M"))
    return "\n".join(lines)


# ─────────────────── 主入口 ───────────────────
def main():
    parser = argparse.ArgumentParser(description="LobsterAI 独立签到脚本（青龙友好）")
    parser.add_argument("--auths", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "lobster2api-src", "auths"),
                        help="auths 目录路径（无环境变量时回退使用）")
    parser.add_argument("--base", default=DEFAULT_BASE, help="上游 API 地址")
    parser.add_argument("--version", default="", help="强制指定客户端版本号")
    parser.add_argument("--only", default="", help="只跑指定 UID 的账号")
    args = parser.parse_args()

    # 强制版本
    if args.version and valid_version(args.version):
        _version_cache.update({"val": args.version, "at": time.time(), "failed": False})

    print("╔════════════════════════════════════╗")
    print("║ 🦞 LobsterAI 独立签到             ║")
    print("╚════════════════════════════════════╝")

    accounts = load_all_accounts(args.auths, args.only)
    if not accounts:
        mode = "环境变量 LOBSTERAI_TOKEN" if os.environ.get("LOBSTERAI_TOKEN", "").strip() else "auths 目录 " + args.auths
        print("❌ 未找到可用账号（来源: %s）" % mode)
        print("   请设置环境变量 LOBSTERAI_TOKEN，格式: uid:AT:RT（每行一个账号）")
        sys.exit(1)

    print("📁 来源: %s" % ("环境变量 LOBSTERAI_TOKEN" if os.environ.get("LOBSTERAI_TOKEN", "").strip() else args.auths))
    print("👥 账号数: %d" % len(accounts))

    # 自动续期
    auto_refresh(accounts, args.base)
    print()

    results = []
    for i, acc in enumerate(accounts):
        r = run_account(i + 1, acc, args.base)
        results.append(r)
        time.sleep(1.5)

    print()
    summary = build_summary(results)
    print(summary)
    send_notify("🦞 LobsterAI 签到报告", summary)


if __name__ == "__main__":
    main()
