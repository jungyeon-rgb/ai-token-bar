# ai-token-bar

Claude.ai / ChatGPT 사용량을 macOS 메뉴 바에서 실시간으로 확인하는 앱.

## 지원 항목

| 항목 | 방식 | 표시 |
|------|------|------|
| Claude.ai 구독 | 웹 세션 쿠키 | 메시지 잔여 % |
| ChatGPT / OpenAI API | API key | 당월 달러 사용량 % |
| Anthropic API | API key + rate-limit 헤더 | 분당 토큰 % |

## 설치

```bash
pip install -r requirements.txt
```

## 설정

처음 실행 시 `~/.config/ai-token-bar/config.yaml`이 자동 생성됩니다.

### Claude.ai 세션 키 추출

1. claude.ai 로그인
2. DevTools → Application → Cookies → `sessionKey` 값 복사
3. `config.yaml`의 `claude_web.session_key`에 입력

### OpenAI API key

- [platform.openai.com](https://platform.openai.com) → API keys에서 발급
- `config.yaml`의 `chatgpt.api_key`에 입력

### Anthropic API key

- [console.anthropic.com](https://console.anthropic.com) → API Keys에서 발급
- `config.yaml`의 `anthropic_api.api_key`에 입력

## 실행

```bash
python3 app.py
```

## 메뉴 바 아이콘 기준

| 아이콘 | 사용량 |
|--------|--------|
| 🟢 | 70% 미만 |
| 🟡 | 70–89% |
| 🔴 | 90% 이상 |

> 메뉴 바 아이콘은 등록된 프로바이더 중 가장 높은 사용량 기준.

## 한계

- Claude.ai 구독 사용량은 내부 API 기반으로 구조 변경 시 동작 안 할 수 있음
- ChatGPT Plus 구독 사용량(chatgpt.com)은 공식 API 없어서 OpenAI API 사용량으로 대체
- Anthropic API 사용량은 분당 rate-limit 기준 (누적 월별 사용량 아님)
