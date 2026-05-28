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
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": "https://claude.ai/",
            "Origin": "https://claude.ai",
            "Accept": "application/json",
        }

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

            # 2. 사용량 조회
            resp = requests.get(
                f"{self.BASE_URL}/organizations/{org_id}/usage",
                cookies=cookies,
                headers=headers,
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            # utilization: 0~100 퍼센트 값
            # seven_day가 주 단위 한도, five_hour가 단기 한도
            seven_day = data.get("seven_day") or {}
            five_hour = data.get("five_hour") or {}

            seven_day_pct = seven_day.get("utilization") or 0.0
            five_hour_pct = five_hour.get("utilization") or 0.0

            # 더 높은 쪽 기준으로 표시
            utilization = max(seven_day_pct, five_hour_pct)
            result = UsageResult(used=utilization, total=100.0, unit="%")
            self.last_usage = result
            return result

        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 401:
                raise RuntimeError("Claude.ai 세션 만료 — sessionKey를 갱신하세요") from e
            raise
        except Exception as e:
            print(f"[ClaudeWeb] {type(e).__name__}: {e}")
            return None
