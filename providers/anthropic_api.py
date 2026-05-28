"""
Anthropic API key 유효성 확인 (models endpoint 기반)

Anthropic은 월별 사용량 공개 API가 없어서 key 유효 여부 + rate-limit 헤더로 표시.
API key: console.anthropic.com → API Keys
"""

import requests
from typing import Optional
from .base import BaseProvider, UsageResult


class AnthropicAPIProvider(BaseProvider):
    name = "Anthropic API"
    MODELS_URL = "https://api.anthropic.com/v1/models"

    def fetch(self) -> Optional[UsageResult]:
        api_key = self.config.get("api_key", "")
        if not api_key:
            return None

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }

        try:
            resp = requests.get(self.MODELS_URL, headers=headers, timeout=10)
            resp.raise_for_status()

            limit = int(resp.headers.get("anthropic-ratelimit-tokens-limit", 0))
            remaining = int(resp.headers.get("anthropic-ratelimit-tokens-remaining", 0))

            if limit > 0:
                used = limit - remaining
                result = UsageResult(used=used, total=limit, unit="tokens/min")
            else:
                result = UsageResult(used=0, total=1, unit="(키 유효)")

            self.last_usage = result
            return result

        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 401:
                raise RuntimeError("Anthropic API key 인증 실패") from e
            raise
        except Exception as e:
            print(f"[AnthropicAPI] {type(e).__name__}: {e}")
            return None
