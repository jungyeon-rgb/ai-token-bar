# ai-token-bar

Claude.ai / ChatGPT 구독 사용량을 macOS 메뉴 바에서 실시간으로 확인하는 앱.

## 지원 항목

| 항목 | 방식 | 표시 |
|------|------|------|
| Claude.ai 구독 | 웹 세션 쿠키 | 7일 사용률 % |
| ChatGPT Plus 구독 | 웹 세션 쿠키 | 구독 사용률 % |
| Anthropic API | API key | 키 유효 여부 |
| OpenAI API | API key | 키 유효 여부 |

> Anthropic / OpenAI API의 월별 토큰 사용량은 공개 endpoint가 없어 구독 사용량과 별개로 조회 불가.

## 설치

```bash
brew install python@3.12
cd ~/ai-token-bar
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 설정

처음 실행 시 `~/.config/ai-token-bar/config.yaml`이 자동 생성됩니다.  
메뉴 바 → "설정 파일 열기"로 열어서 아래 항목을 채웁니다.

### Claude.ai 세션 키

1. chrome에서 claude.ai 로그인
2. `F12` → Application → Cookies → `https://claude.ai`
3. `sessionKey` 값 복사 → `claude_web.session_key`

### ChatGPT Plus 세션 토큰

1. chatgpt.com 로그인
2. `F12` → Application → Cookies → `https://chatgpt.com`
3. `__Secure-next-auth.session-token` 값 복사 → `chatgpt_web.session_token`

### Anthropic / OpenAI API key (선택)

- Anthropic: console.anthropic.com → API Keys → `anthropic_api.api_key`
- OpenAI: platform.openai.com → API keys → `openai_api.api_key`

## 실행

```bash
source .venv/bin/activate
python app.py
```

## 메뉴 바 아이콘 기준

| 아이콘 | 사용량 |
|--------|--------|
| 🟢 | 70% 미만 |
| 🟡 | 70–89% |
| 🔴 | 90% 이상 |

메뉴 바 아이콘은 등록된 프로바이더 중 가장 높은 사용량 기준.
