"""
Claude.ai 구독 사용량 (웹 세션 기반)

세션 키 추출 방법:
  1. claude.ai 로그인 후 DevTools → Application → Cookies
  2. `sessionKey` 값 복사 → config.yaml의 claude_web.session_key에 입력
"""

import requests
from typing import Optional
from .base import BaseProvider, UsageResult


class ClaudeWebProvider(BaseProvider):
    name = "Claude.ai"
    BASE_URL = "https://claude.ai/api"

    def fetch(self) -> Optional[UsageResult]:
        session_key = self.config.get("session_key", "")
        if not session_key:
            return None

        cookies = {"sessionKey": session_key}
        headers = {"Content-Type": "application/json"}

        try:
            # 1. 소속 org ID 조회
            resp = requests.get(
                f"{self.BASE_URL}/organizations",
                cookies=cookies,
                headers=headers,
                timeout=10,
            )
            resp.raise_for_status()
            orgs = resp.json()
            if not orgs:
                return None
            org_id = orgs[0]["uuid"]

            # 2. 사용량 제한 조회
            resp = requests.get(
                f"{self.BASE_URL}/organizations/{org_id}/limits",
                cookies=cookies,
                headers=headers,
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            # 응답 구조: {"messages_remaining": N, "messages_limit": N} 형태 추정
            # Claude Pro는 하루/주 단위 메시지 제한이 있음
            limit = data.get("messages_limit") or data.get("limit")
            remaining = data.get("messages_remaining") or data.get("remaining")

            if limit is None or remaining is None:
                return None

            used = limit - remaining
            result = UsageResult(used=used, total=limit, unit="messages")
            self.last_usage = result
            return result

        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 401:
                raise RuntimeError("Claude.ai 세션 만료 — sessionKey를 갱신하세요") from e
            raise
        except Exception:
            return None
