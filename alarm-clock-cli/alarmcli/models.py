"""Data model for a single alarm."""
from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class Alarm:
    id: int
    time: str  # 24-hour "HH:MM"
    label: str = ""
    enabled: bool = True
    repeat: List[int] = field(default_factory=list)  # 0=Mon ... 6=Sun, empty = one-time

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Alarm":
        return Alarm(
            id=d["id"],
            time=d["time"],
            label=d.get("label", ""),
            enabled=d.get("enabled", True),
            repeat=d.get("repeat", []),
        )