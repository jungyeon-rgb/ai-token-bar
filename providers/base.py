from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class UsageResult:
    used: float
    total: float
    unit: str = ""

    @property
    def percent(self) -> float:
        return (self.used / self.total * 100) if self.total > 0 else 0.0

    def label(self) -> str:
        if self.unit == "usd":
            return f"${self.used:.2f} / ${self.total:.2f}"
        if self.unit == "messages":
            return f"{int(self.used)} / {int(self.total)} 메시지"
        if self.unit == "%":
            return f"{self.used:.0f}% 사용"
        if self.unit == "(키 유효)":
            return "키 유효"
        return f"{int(self.used):,} / {int(self.total):,} {self.unit}"


class BaseProvider(ABC):
    name: str

    def __init__(self, config: dict):
        self.config = config
        self.last_usage: Optional[UsageResult] = None

    @abstractmethod
    def fetch(self) -> Optional[UsageResult]:
        """최신 사용량을 가져와서 last_usage에 저장 후 반환"""
        pass
