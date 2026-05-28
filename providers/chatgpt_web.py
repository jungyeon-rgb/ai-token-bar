"""
ChatGPT Plus 구독 사용량 (chatgpt.com 세션 기반)

세션 토큰 추출 방법:
  1. chatgpt.com 로그인 후 DevTools → Application → Cookies
  2. `__Secure-next-auth.session-token` 값 복사
  3. config.yaml의 chatgpt_web.session_token에 입력
"""

import requests
from typing import Optional
from .base import BaseProvider, UsageResult


class ChatGPTWebProvider(BaseProvider):
    name = "ChatGPT"
    BASE_URL = "https://chatgpt.com/backend-api"

    def fetch(self) -> Optional[UsageResult]:
        session_token = self.config.get("session_token", "")
        if not session_token:
            return None

        cookies = {"__Secure-next-auth.session-token": session_token}
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": "https://chatgpt.com/",
            "Accept": "application/json",
        }

        try:
            # 세션으로 access token 획득
            session_resp = requests.get(
                "https://chatgpt.com/api/auth/session",
                cookies=cookies,
                headers=headers,
                timeout=10,
            )
            session_resp.raise_for_status()
            session_data = session_resp.json()
            access_token = session_data.get("accessToken")

            if not access_token:
                print("[ChatGPT] accessToken 없음 — 세션 토큰을 확인하세요")
                return None

            auth_headers = {**headers, "Authorization": f"Bearer {access_token}"}

            # 계정 정보 및 사용량 조회
            me_resp = requests.get(
                f"{self.BASE_URL}/me",
                headers=auth_headers,
                timeout=10,
            )
            me_resp.raise_for_status()
            print(f"[ChatGPT] me keys: {list(me_resp.json().keys())}")

            # 구독/사용량 endpoint 탐색
            for path in ["/accounts/check/v4-2023-04-27", "/usage", "/subscription"]:
                r = requests.get(
                    f"{self.BASE_URL}{path}",
                    headers=auth_headers,
                    timeout=10,
                )
                print(f"[ChatGPT] {path} → {r.status_code}")
                if r.status_code == 200:
                    data = r.json()
                    print(f"[ChatGPT] {path} 응답: {data}")
                    break

            return None  # endpoint 확인 후 파싱 로직 추가 예정

        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 401:
                raise RuntimeError("ChatGPT 세션 만료 — session_token을 갱신하세요") from e
            raise
        except Exception as e:
            print(f"[ChatGPT] {type(e).__name__}: {e}")
            return None
