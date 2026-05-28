"""
OpenAI API 사용량 (rate-limit 헤더 기반)

ChatGPT Plus / OpenAI API 공통.
일반 API key로 모델 목록 조회 시 응답 헤더에서 rate-limit 정보를 읽음.

API key 발급: platform.openai.com → API keys
"""

import requests
from typing import Optional
from .base import BaseProvider, UsageResult


class ChatGPTWebProvider(BaseProvider):
    name = "OpenAI"
    PROBE_URL = "https://api.openai.com/v1/models"

    def fetch(self) -> Optional[UsageResult]:
        api_key = self.config.get("api_key", "")
        if not api_key:
            return None

        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            resp = requests.get(self.PROBE_URL, headers=headers, timeout=10)
            resp.raise_for_status()

            limit = int(resp.headers.get("x-ratelimit-limit-tokens", 0))
            remaining = int(resp.headers.get("x-ratelimit-remaining-tokens", 0))

            if limit == 0:
                # rate-limit 헤더 없는 경우 — key 유효 확인만 표시
                result = UsageResult(used=0, total=1, unit="(키 유효)")
                self.last_usage = result
                return result

            used = limit - remaining
            result = UsageResult(used=used, total=limit, unit="tokens/min")
            self.last_usage = result
            return result

        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 401:
                raise RuntimeError("OpenAI API key 인증 실패") from e
            raise
        except Exception as e:
            print(f"[OpenAI] {type(e).__name__}: {e}")
            return None
