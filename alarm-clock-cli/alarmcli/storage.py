"""JSON file persistence for alarms."""
import json
import os
from typing import List

from .models import Alarm

DEFAULT_PATH = os.path.expanduser("~/.alarmcli/alarms.json")


def _ensure_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def load_alarms(path: str = DEFAULT_PATH) -> List[Alarm]:
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []
    return [Alarm.from_dict(d) for d in data]


def save_alarms(alarms: List[Alarm], path: str = DEFAULT_PATH) -> None:
    _ensure_dir(path)
    with open(path, "w") as f:
        json.dump([a.to_dict() for a in alarms], f, indent=2)


def next_id(alarms: List[Alarm]) -> int:
    return max((a.id for a in alarms), default=0) + 1