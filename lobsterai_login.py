#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔑 LobsterAI Token 获取工具
════════════════════════════════════════════════════════════

📌 从 LobsterAI 桌面客户端本地数据库读取 accessToken + refreshToken。
   桌面端登录后 token 存储在 %APPDATA%/LobsterAI/lobsterai.sqlite → kv 表 → auth_tokens。

✨ 支持方式
   1. 桌面客户端读取（推荐，一键获取）
   2. 手动粘贴 token（F12 抓包方式）

🚀 使用方法
   python lobsterai_login.py                   # 自动从桌面端读取
   python lobsterai_login.py --manual          # 手动粘贴 AT 和 RT
   python lobsterai_login.py --export          # 输出为环境变量格式（可直接粘贴到青龙）

🔑 输出格式（用于 LOBSTERAI_TOKEN 环境变量）
   uid:AT:RT

💡 前提
   方式 1：电脑上已安装并登录 LobsterAI 桌面客户端
   方式 2：浏览器登录 https://lobsterai.youdao.com/portal#/login
           → F12 → Network → 找到带 Authorization: Bearer eyJ... 的请求
           → 复制 Bearer 后面的 accessToken
           → 再找一个带 refreshToken 或 cookie 里的 refreshToken

📄 依赖：仅标准库（sqlite3 是内置的）
"""
import sys, os, json, sqlite3, base64, argparse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# LobsterAI 桌面端 sqlite 路径（Windows）
SQLITE_PATHS = [
    Path(os.environ.get("APPDATA", "")) / "LobsterAI" / "lobsterai.sqlite",
    Path(os.environ.get("LOCALAPPDATA", "")) / "LobsterAI" / "lobsterai.sqlite",
    Path.home() / ".config" / "LobsterAI" / "lobsterai.sqlite",
    Path.home() / ".lobsterai" / "lobsterai.sqlite",
]


def jwt_payload(token):
    """解码 JWT payload。"""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {}
        payload = parts[1] + "=" * (4 - len(parts[1]) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception:
        return {}


def jwt_exp(token):
    return jwt_payload(token).get("exp", 0)


def jwt_sub(token):
    return str(jwt_payload(token).get("sub", ""))


def read_desktop_tokens():
    """从 LobsterAI 桌面端 sqlite 读取 auth_tokens。返回 dict 或 None。"""
    for path in SQLITE_PATHS:
        if not path.is_file():
            continue
        try:
            db = sqlite3.connect(str(path))
            c = db.cursor()
            c.execute("SELECT value FROM kv WHERE key = ?", ("auth_tokens",))
            row = c.fetchone()
            db.close()
            if row:
                return json.loads(row[0])
        except Exception as e:
            print("⚠️ 读取 %s 失败: %s" % (path, str(e)[:80]))
    return None


def read_manual_tokens():
    """手动粘贴 AT 和 RT。"""
    print("📋 手动输入 Token")
    print("   AT = accessToken（浏览器 F12 → Network → 找 Authorization: Bearer eyJ... ）")
    print("   RT = refreshToken（F12 → Application → Cookies 或 LocalStorage）")
    print()
    at = input("粘贴 accessToken (eyJ...): ").strip()
    rt = input("粘贴 refreshToken (eyJ...，可为空): ").strip()
    if not at:
        return None
    return {"accessToken": at, "refreshToken": rt or ""}


def format_output(uid, at, rt, export=False):
    """格式化输出。export=True 时输出纯 uid:AT:RT 格式。"""
    if export:
        return "%s:%s:%s" % (uid, at, rt)
    return {
        "uid": uid,
        "accessToken": at,
        "refreshToken": rt,
    }


def show_result(at, rt, export=False):
    """展示结果。"""
    uid = jwt_sub(at)
    exp = jwt_exp(at)
    exp_str = ""
    if exp:
        import time as _t
        remaining = (exp - _t.time()) / 86400
        if remaining > 0:
            exp_str = "（剩余 %.1f 天）" % remaining
        else:
            exp_str = "（已过期 %.1f 天）" % -remaining
    else:
        exp_str = "（无法解析过期时间）"

    if export:
        print(format_output(uid, at, rt, export=True))
    else:
        print()
        print("✅ Token 获取成功!")
        print("   UID:         %s" % uid)
        print("   AT 有效期:   %s" % exp_str)
        print("   AT:          %s" % at[:50] + "..." if len(at) > 50 else at)
        print("   RT:          %s" % (rt[:50] + "..." if len(rt) > 50 else rt))
        print()
        print("🦞 青龙环境变量 LOBSTERAI_TOKEN 值:")
        print("   " + format_output(uid, at, rt, export=True))


def main():
    parser = argparse.ArgumentParser(description="LobsterAI Token 获取工具")
    parser.add_argument("--manual", action="store_true", help="手动粘贴 token（F12 抓包）")
    parser.add_argument("--export", action="store_true", help="仅输出 uid:AT:RT 格式（用于青龙）")
    args = parser.parse_args()

    if not args.export:
        print("╔════════════════════════════════════╗")
        print("║ 🔑 LobsterAI Token 获取           ║")
        print("╚════════════════════════════════════╝")
        print()

    if args.manual:
        data = read_manual_tokens()
    else:
        if not args.export:
            print("🔍 扫描 LobsterAI 桌面端...")
        data = read_desktop_tokens()
        if not data:
            if not args.export:
                print("   ❌ 未找到 LobsterAI 桌面端数据库")
                print("   💡 可能原因:")
                print("      1. 未安装 LobsterAI 桌面客户端")
                print("      2. 已安装但未登录过")
                print("      3. 数据库路径不在默认位置")
                print()
                print("   尝试手动方式: python lobsterai_login.py --manual")
            data = read_manual_tokens()
            if not data or not data.get("accessToken"):
                if args.export:
                    print("❌ 获取 token 失败")
                    sys.exit(1)
                sys.exit(1)

    show_result(data["accessToken"], data.get("refreshToken", ""), args.export)


if __name__ == "__main__":
    main()
