#!/usr/bin/env python3
import os
import threading
from typing import Optional

import rumps

from config import load_config, CONFIG_PATH
from providers import (
    AnthropicAPIProvider,
    BaseProvider,
    ClaudeWebProvider,
    ChatGPTWebProvider,
    UsageResult,
)

REFRESH_INTERVAL = 300  # 5분


def _usage_icon(result: Optional[UsageResult]) -> str:
    if result is None:
        return "–"
    if result.percent >= 90:
        return "🔴"
    if result.percent >= 70:
        return "🟡"
    return "🟢"


class AITokenBar(rumps.App):
    def __init__(self):
        super().__init__("AI", quit_button=None)
        self._providers: list[BaseProvider] = []
        self._menu_items: dict[str, rumps.MenuItem] = {}
        self._error_item = rumps.MenuItem("설정 파일이 없거나 비어 있습니다")
        self._setup()

    def _setup(self):
        config = load_config()
        self._providers.clear()

        if config.get("claude_web", {}).get("session_key"):
            self._providers.append(ClaudeWebProvider(config["claude_web"]))

        if config.get("chatgpt", {}).get("api_key"):
            self._providers.append(ChatGPTWebProvider(config["chatgpt"]))

        if config.get("anthropic_api", {}).get("api_key"):
            self._providers.append(AnthropicAPIProvider(config["anthropic_api"]))

        self.menu.clear()

        if not self._providers:
            self.menu.add(self._error_item)
        else:
            for p in self._providers:
                item = rumps.MenuItem(f"{p.name}: 로딩 중…")
                self._menu_items[p.name] = item
                self.menu.add(item)

        self.menu.add(None)
        self.menu.add(rumps.MenuItem("새로고침", callback=self.on_refresh))
        self.menu.add(rumps.MenuItem("설정 파일 열기", callback=self.on_open_config))
        self.menu.add(None)
        self.menu.add(rumps.MenuItem("종료", callback=rumps.quit_application))

        self._timer = rumps.Timer(self.on_refresh, REFRESH_INTERVAL)
        self._timer.start()
        self.on_refresh(None)

    def on_refresh(self, _):
        def _run():
            for p in self._providers:
                try:
                    result = p.fetch()
                    item = self._menu_items.get(p.name)
                    if item is None:
                        continue
                    if result:
                        icon = _usage_icon(result)
                        item.title = f"{icon} {p.name}: {result.percent:.0f}%  ({result.label()})"
                    else:
                        item.title = f"❓ {p.name}: 조회 실패"
                except RuntimeError as e:
                    item = self._menu_items.get(p.name)
                    if item:
                        item.title = f"⚠️ {p.name}: {e}"
                except Exception:
                    item = self._menu_items.get(p.name)
                    if item:
                        item.title = f"⚠️ {p.name}: 오류"

            self._update_title_icon()

        threading.Thread(target=_run, daemon=True).start()

    def _update_title_icon(self):
        results = [p.last_usage for p in self._providers]
        valid = [r for r in results if r is not None]
        if not valid:
            self.title = "AI"
            return
        max_pct = max(r.percent for r in valid)
        if max_pct >= 90:
            self.title = "🔴"
        elif max_pct >= 70:
            self.title = "🟡"
        else:
            self.title = "🟢"

    def on_open_config(self, _):
        os.system(f"open '{CONFIG_PATH}'")


if __name__ == "__main__":
    AITokenBar().run()
