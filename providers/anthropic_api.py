"""
Anthropic API 사용량 (API key 기반)

Anthropic은 공개 usage endpoint가 없어서 응답 헤더의 rate-limit 정보로 추적.
  x-ratelimit-limit-tokens, x-ratelimit-remaining-tokens (분당 기준)

더 정확한 누적 사용량이 필요하면 anthropic.com/console → Usage 탭 직접 확인 권장.

API key 발급: console.anthropic.com → API Keys
"""

import requests
from typing import Optional
from .base import BaseProvider, UsageResult


class AnthropicAPIProvider(BaseProvider):
    name = "Anthropic API"
    # 간단한 probe 요청으로 rate-limit 헤더를 읽어옴
    PROBE_URL = "https://api.anthropic.com/v1/messages"

    def fetch(self) -> Optional[UsageResult]:
        api_key = self.config.get("api_key", "")
        if not api_key:
            return None

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        # 최소 토큰 소모로 헤더만 확인
        probe_body = {
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "1"}],
        }

        try:
            resp = requests.post(
                self.PROBE_URL, headers=headers, json=probe_body, timeout=15
            )
            resp.raise_for_status()

            limit = int(resp.headers.get("x-ratelimit-limit-tokens", 0))
            remaining = int(resp.headers.get("x-ratelimit-remaining-tokens", 0))

            if limit == 0:
                return None

            used = limit - remaining
            result = UsageResult(used=used, total=limit, unit="tokens/min")
            self.last_usage = result
            return result

        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 401:
                raise RuntimeError("Anthropic API key 인증 실패") from e
            raise
        except Exception:
            return None
