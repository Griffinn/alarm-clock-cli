import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from alarmcli.cli import parse_repeat, validate_time
from alarmcli.models import Alarm
from alarmcli.storage import load_alarms, next_id, save_alarms


def test_alarm_roundtrip_dict():
    a = Alarm(id=1, time="07:30", label="Wake up", enabled=True, repeat=[0, 2, 4])
    d = a.to_dict()
    b = Alarm.from_dict(d)
    assert a == b


def test_save_and_load_alarms():
    path = os.path.join(tempfile.mkdtemp(), "alarms.json")
    alarms = [Alarm(id=1, time="06:00", label="Gym")]
    save_alarms(alarms, path)
    loaded = load_alarms(path)
    assert len(loaded) == 1
    assert loaded[0].time == "06:00"
    assert loaded[0].label == "Gym"


def test_load_alarms_missing_file_returns_empty():
    path = os.path.join(tempfile.mkdtemp(), "does_not_exist.json")
    assert load_alarms(path) == []


def test_next_id_increments():
    alarms = [Alarm(id=1, time="06:00"), Alarm(id=3, time="07:00")]
    assert next_id(alarms) == 4
    assert next_id([]) == 1


def test_parse_repeat_valid():
    assert parse_repeat("mon,wed,fri") == [0, 2, 4]
    assert parse_repeat("") == []


def test_parse_repeat_invalid():
    try:
        parse_repeat("funday")
        assert False, "should have raised"
    except Exception:
        pass


def test_validate_time():
    assert validate_time("07:30") == "07:30"
    try:
        validate_time("25:99")
        assert False, "should have raised"
    except Exception:
        pass


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))