#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LobsterAI SMS 验证码登录（Playwright 版）
输出 uid:AT:RT（直接粘贴到青龙 LOBSTERAI_TOKEN）

用法:
  python lobsterai_sms.py 13800138000
  python lobsterai_sms.py
  python lobsterai_sms.py --headless   (不推荐，滑块需手动拖)

依赖: pip install playwright && playwright install chromium
"""
import sys, os, json, time, base64, argparse, secrets, string, threading, uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("pip install playwright && playwright install chromium")
    sys.exit(1)

import requests

UPSTREAM = "https://lobsterai-server.youdao.com"
PORTAL = "https://lobsterai.youdao.com"
CALLBACK_PORT = 18368
SEL_PHONE = "input[name='email']"
SEL_CODE = "input[name='phonecode']"
SEL_SEND = "a.j-power-btn"
SEL_LOGIN = "a.u-loginbtn"
SEL_CHECKBOX = "input[type='checkbox']"


def jwt_sub(tok):
    try:
        p = tok.split(".")[1]; p += "=" * (4 - len(p) % 4)
        return str(json.loads(base64.urlsafe_b64decode(p)).get("sub", ""))
    except Exception:
        return ""


def jwt_exp_str(tok):
    try:
        p = tok.split(".")[1]; p += "=" * (4 - len(p) % 4)
        exp = int(json.loads(base64.urlsafe_b64decode(p)).get("exp", 0))
        rem = (exp - time.time()) / 86400
        return "剩余 %.0f 天" % rem if rem > 0 else "已过期"
    except Exception:
        return "?"


class CB(BaseHTTPRequestHandler):
    code = None
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        CB.code = q.get("code", [""])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write("OK".encode())
    def log_message(self, *a):
        pass


def start_cb(port):
    srv = HTTPServer(("0.0.0.0", port), CB)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def do_login(phone, headless=False, port=CALLBACK_PORT):
    state = "".join(secrets.choice(string.hexdigits) for _ in range(32))
    install_uuid = str(uuid.uuid4())
    login_url = "%s/portal#/login?source=electron&redirect_uri=http://127.0.0.1:%d/auth/callback&state=%s" % (PORTAL, port, state)
    srv = start_cb(port)
    print("  %s" % phone)
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        page = ctx.new_page()

        print("[1/4] 打开登录页...")
        page.goto(login_url, wait_until="networkidle", timeout=30000)
        time.sleep(3)

        urs = None
        for f in page.frames:
            if "passport.youdao.com" in f.url:
                urs = f
                break
        if not urs:
            print("URS iframe not found")
            page.screenshot(path="debug.png")
            browser.close()
            return None

        print("[2/4] 填手机号 + 勾协议...")
        urs.locator(SEL_PHONE).first.fill(phone)
        time.sleep(0.3)
        try:
            cb = urs.locator(SEL_CHECKBOX).first
            if cb.is_visible() and not cb.is_checked():
                cb.check()
        except Exception:
            pass
        time.sleep(0.3)

        print("[3/4] 请在浏览器中手动完成以下操作：")
        print("     1. 点击「获取验证码」")
        print("     2. 拖动滑块到正确位置")
        print("     3. 等手机收到验证码")
        print()
        print("     浏览器窗口已打开，完成后回到这里输入验证码。")
        print()
        print("     等待短信发送确认...")

        sms_sent = False
        for i in range(120):
            time.sleep(1)
            try:
                content = urs.locator("body").text_content() or ""
                if "秒" in content and ("重新" in content or "重发" in content):
                    print("     OK 短信已发送!")
                    sms_sent = True
                    break
            except Exception:
                pass
            if i % 15 == 14:
                print("     ... %ds" % (i + 1))

        if not sms_sent:
            print("     未自动检测到发送，继续...")

        sms_code = input("\n[4/4] 请输入收到的验证码: ").strip()
        if not sms_code:
            print("未输入验证码")
            browser.close()
            return None

        for f in page.frames:
            if "passport.youdao.com" in f.url:
                urs = f
                break

        urs.locator(SEL_CODE).first.fill(sms_code)
        time.sleep(0.3)
        urs.locator(SEL_LOGIN).first.click()
        print("    已提交")

        print("    Waiting for login result...")
        login_ok = False
        for i in range(20):
            time.sleep(1)
            if CB.code:
                login_ok = True
                print("    OK callback received!")
                break
            try:
                cur_url = page.url
                if "#/login" not in cur_url and "passport" not in cur_url:
                    login_ok = True
                    print("    Page navigated: %s" % cur_url[:100])
                    break
                urs_gone = True
                for f in page.frames:
                    if "passport.youdao.com" in f.url:
                        urs_gone = False
                        break
                if urs_gone and i > 3:
                    login_ok = True
                    print("    URS iframe closed - login succeeded!")
                    break
            except Exception:
                pass
        if not login_ok:
            print("    WARN: no clear navigation, checking cookies anyway...")

        cookies = ctx.cookies()
        cookie_dict = {c["name"]: c["value"] for c in cookies}
        p_info = cookie_dict.get("P_INFO", "")
        dict_sess = cookie_dict.get("DICT_SESS", "")
        web_sess = cookie_dict.get("lobsterai_web_session", "")
        print("    P_INFO: %s" % ("YES" if p_info else "no"))
        print("    DICT_SESS: %s" % ("YES" if dict_sess else "no"))
        print("    web_session: %s" % ("YES" if web_sess else "no"))

        browser.close()

    srv.shutdown()

    result = None
    if CB.code:
        print("\n[exchange via code]...")
        try:
            now_ms = str(int(time.time() * 1000))
            r = requests.post(UPSTREAM + "/api/auth/exchange",
                              json={"authCode": CB.code, "firstKeyfrom": now_ms,
                                    "latestKeyfrom": now_ms, "uuid": install_uuid, "version": "0.1.0"},
                              headers={"Content-Type": "application/json"}, timeout=30)
            d = r.json()
            if d.get("code", -1) == 0:
                data = d.get("data") or {}
                at = data.get("accessToken", "")
                rt = data.get("refreshToken", "")
                user = data.get("user") or {}
                uid = str(user.get("id") or user.get("userId") or "") or jwt_sub(at)
                result = {"uid": uid, "at": at, "rt": rt, "nickname": user.get("nickname", "")}
        except Exception as e:
            print("    code exchange failed: %s" % str(e)[:80])

    if not result and (p_info or dict_sess):
        print("\n[exchange via cookies -> authCode -> JWT]...")
        try:
            r1 = requests.post(UPSTREAM + "/api/auth/callback",
                               json={"source": "electron", "username": phone},
                               timeout=15, cookies=cookie_dict,
                               headers={"Content-Type": "application/json",
                                        "Origin": "https://lobsterai.youdao.com"})
            d1 = r1.json()
            auth_code = (d1.get("data") or {}).get("authCode", "")
            if not auth_code:
                print("    authCode: FAILED (%s)" % str(d1.get("msg", ""))[:60])
            else:
                print("    authCode: %s..." % auth_code[:20])
                now_ms = str(int(time.time() * 1000))
                r2 = requests.post(UPSTREAM + "/api/auth/exchange", json={
                    "authCode": auth_code, "firstKeyfrom": now_ms,
                    "latestKeyfrom": now_ms, "uuid": str(uuid.uuid4()), "version": "0.1.0"
                }, headers={"Content-Type": "application/json"}, timeout=15)
                d2 = r2.json()
                data = d2.get("data") or {}
                at = data.get("accessToken", "")
                rt = data.get("refreshToken", "")
                user = data.get("user") or {}
                uid = str(user.get("id") or user.get("userId") or "")
                if at:
                    result = {"uid": uid, "at": at, "rt": rt, "nickname": user.get("nickname", "")}
                    print("    JWT obtained!")
                else:
                    print("    exchange: no accessToken (%s)" % str(d2.get("msg", ""))[:60])
        except Exception as e:
            print("    error: %s" % str(e)[:80])

    if not result:
        print("\nNo JWT obtained.")
        return None

    print("\nOK %s (%s)" % (result["uid"], result.get("nickname", "")))
    print("   AT %s (%s)" % (result["at"][:30], jwt_exp_str(result["at"])))
    print("   RT %s..." % result["rt"][:30])
    print()
    print("LOBSTERAI_TOKEN:")
    print("   %s:%s:%s" % (result["uid"], result["at"], result["rt"]))
    return result


def main():
    parser = argparse.ArgumentParser(description="LobsterAI SMS")
    parser.add_argument("phone", nargs="?", default="")
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()
    phone = args.phone or input("手机号: ").strip()
    if not phone:
        sys.exit(1)
    result = do_login(phone, headless=args.headless)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
