"""
ChatGPT Plus 구독 사용량 (OpenAI 플랫폼 API 기반)

ChatGPT Plus는 공식 사용량 API가 없어서 OpenAI Platform API key로
당월 API 사용량(달러)을 조회하는 방식으로 우회.

API key 발급: platform.openai.com → API keys
  - 구독 사용량(chatgpt.com)이 아닌 API 토큰 사용량 기준임을 참고.
"""

import requests
from datetime import date, timedelta
from typing import Optional
from .base import BaseProvider, UsageResult


class ChatGPTWebProvider(BaseProvider):
    name = "ChatGPT"
    USAGE_URL = "https://api.openai.com/dashboard/billing/usage"
    SUBSCRIPTION_URL = "https://api.openai.com/dashboard/billing/subscription"

    def fetch(self) -> Optional[UsageResult]:
        api_key = self.config.get("api_key", "")
        if not api_key:
            return None

        headers = {"Authorization": f"Bearer {api_key}"}
        today = date.today()
        start = today.replace(day=1)  # 이번 달 1일
        end = today + timedelta(days=1)

        try:
            # 당월 한도 조회
            sub_resp = requests.get(
                self.SUBSCRIPTION_URL, headers=headers, timeout=10
            )
            sub_resp.raise_for_status()
            sub = sub_resp.json()
            hard_limit_usd = sub.get("hard_limit_usd") or sub.get("system_hard_limit_usd", 0)

            # 당월 사용량 조회
            usage_resp = requests.get(
                self.USAGE_URL,
                headers=headers,
                params={
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat(),
                },
                timeout=10,
            )
            usage_resp.raise_for_status()
            usage_data = usage_resp.json()
            total_usage_cents = usage_data.get("total_usage", 0)
            used_usd = total_usage_cents / 100.0

            result = UsageResult(used=used_usd, total=float(hard_limit_usd), unit="usd")
            self.last_usage = result
            return result

        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 401:
                raise RuntimeError("OpenAI API key 인증 실패") from e
            raise
        except Exception:
            return None
