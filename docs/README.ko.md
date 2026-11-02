# 🦞 LobsterAI AutoCheckin

**LobsterAI 데일리 체크인을 위한 데스크톱 자격 증명 추출, SMS 로그인, 멀티 계정, 토큰 갱신 및 선택적 알림 도구입니다.**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

> 전체 중국어 문서는 [../README.md](../README.md)에서 확인할 수 있습니다.

## 개요

LobsterAI AutoCheckin은 하나 이상의 LobsterAI 계정에서 매일 보상을 받습니다. slot과 context를 읽고 체크인을 제출한 뒤 context를 다시 읽어 결과를 검증합니다. 실행 결과는 수령 성공, 오늘 이미 수령, 상류에서 활동 미제공, 요청 오류로 구분됩니다.

저장소에는 세 스크립트가 있습니다. `lobsterai_checkin.py`는 매일 체크인, `lobsterai_login.py`는 데스크톱 클라이언트에서 자격 증명 추출, `lobsterai_sms.py`는 선택적 Playwright SMS 로그인을 담당합니다. 체크인과 데스크톱 추출에는 `requests`만 필요하며 Playwright는 SMS 로그인 전용입니다.

## 핵심 기능

- `slot → context → check_in → context` 순서로 체크인합니다.
- `LOBSTERAI_TOKEN`으로 여러 계정을 지원합니다.
- AT 만료가 7일 이내일 때 RT로 자동 갱신합니다.
- 교체된 토큰을 `lb_refresh_tokens.json`에 저장합니다.
- 이미 수령한 상태와 활동 미제공 상태를 새 보상으로 처리하지 않습니다.
- 공식 업데이트 API에서 클라이언트 버전을 가져오며 수동 지정도 지원합니다.
- PushPlus 알림을 선택적으로 보내고 일반 로그에서 자격 증명을 마스킹합니다.

## 자격 증명 준비

각 계정은 `uid:AT:RT` 형식입니다. AT만 사용할 수 있지만 만료 후 자동 갱신은 되지 않습니다.

### 데스크톱 추출

LobsterAI 데스크톱 클라이언트에 로그인한 뒤 실행합니다.

```bash
python lobsterai_login.py
python lobsterai_login.py --export
```

Windows에서는 `%APPDATA%/LobsterAI/lobsterai.sqlite`를 읽고 `kv.auth_tokens`에서 `accessToken`과 `refreshToken`을 가져옵니다. `--export`는 바로 사용할 수 있는 `uid:AT:RT` 한 줄만 출력합니다.

### SMS 로그인

```bash
pip install playwright
playwright install chromium
python lobsterai_sms.py
python lobsterai_sms.py 138xxxxxxxx
python lobsterai_sms.py --headless 138xxxxxxxx
```

화면 안내에 따라 슬라이더와 SMS 인증번호를 완료하면 로그인 결과에서 `uid:AT:RT`를 생성합니다. 예시 전화번호는 명령 형식 설명용입니다.

## 최소 Qinglong 설정

1. `lobsterai_checkin.py`를 업로드합니다.
2. `pip3 install requests`로 체크인 의존성을 설치합니다.
3. 환경 변수를 추가합니다.

```text
LOBSTERAI_TOKEN=UID_VALUE:AT_VALUE:RT_VALUE
```

4. 예약 작업 명령을 설정합니다.

```bash
task lobsterai_checkin.py
```

권장 cron:

```cron
0 9 * * *
```

여러 계정은 줄바꿈 또는 `@`로 구분합니다. 알림이 필요할 때만 `PUSHPLUS_TOKEN`을 추가합니다.

## 최소 GitHub Actions 설정

**Settings → Secrets and variables → Actions**에 다음 Secrets를 추가합니다.

| Secret | 필수 | 용도 |
| :--- | :---: | :--- |
| `LOBSTERAI_TOKEN` | 예 | 하나 이상의 `uid:AT:RT` 항목 |
| `PUSHPLUS_TOKEN` | 선택 | PushPlus 알림 토큰 |

먼저 **Actions → LobsterAI Daily → Run workflow**를 실행합니다. 포함된 일정은 UTC `0 1 * * *`이며 베이징 시간 매일 09:00입니다. Fork 후 예약 워크플로가 비활성화되어 있으면 Actions 화면에서 활성화합니다.

`lb_refresh_tokens.json` 저장은 비공개 저장소에서만 수행됩니다. 공개 저장소는 교체된 RT를 공개 기록에 남기지 않도록 이 단계를 건너뜁니다. 공개 저장소에서는 매 실행마다 유효한 Secret이 필요합니다.

## 주요 환경 변수

| 변수 | 필수 | 설명 |
| :--- | :---: | :--- |
| `LOBSTERAI_TOKEN` | 예 | `uid:AT:RT` 형식의 멀티 계정 자격 증명 |
| `PUSHPLUS_TOKEN` | 선택 | 결과 요약을 보내는 PushPlus 토큰 |

## 명령행 옵션

| 체크인 옵션 | 동작 |
| :--- | :--- |
| 없음 | 모든 계정 실행 |
| `--only UID` | 지정한 UID만 실행 |
| `--version VERSION` | 클라이언트 버전 강제 지정 |
| `--auths PATH` | 환경 변수가 없을 때 로컬 auth 디렉터리 사용 |
| `--base URL` | API 기본 URL 재정의 |

| 로그인 옵션 | 동작 |
| :--- | :--- |
| `--export` | `uid:AT:RT`만 출력 |
| `--manual` | 자격 증명 직접 붙여넣기 |
| `--headless` | SMS 브라우저 로그인을 화면 없이 실행 |

## 검증 방식

체크인 제출 후 계정 context를 다시 읽습니다. HTTP 200만으로 성공 처리하지 않고 갱신된 `claimedToday` 상태를 기준으로 판정합니다. 한 계정의 실패는 나머지 계정 실행을 중단하지 않습니다. `lb_refresh_tokens.json`에는 실제 자격 증명이 있으므로 공개 저장소에 커밋하지 마세요.

## 개인정보 보호

자격 증명은 환경 변수, Secrets 또는 로컬 클라이언트 저장소에서만 읽습니다. 데이터베이스, 내보낸 AT/RT, SMS 인증번호, `lb_refresh_tokens.json`, 마스킹되지 않은 로그를 공개하지 마세요. Issue에 첨부하기 전 계정 식별자가 남아 있는지 직접 확인해야 합니다.

## 링크

- [Releases](https://github.com/L0NE-6/LobsterAI-AutoCheckin/releases)
- [Issues](https://github.com/L0NE-6/LobsterAI-AutoCheckin/issues)
- [중국어 README](../README.md)
- [변경 기록](../CHANGELOG.md)

## 면책 조항

이 프로젝트는 개인 학습과 자동화를 위한 것입니다. LobsterAI, NetEase Youdao 및 관련 서비스 약관을 확인하고 사용 위험은 사용자 본인이 부담하세요.
