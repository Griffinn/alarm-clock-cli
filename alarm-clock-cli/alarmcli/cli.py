"""Command-line entrypoint for alarmcli."""
import argparse
import re

from .models import Alarm
from .scheduler import run_loop
from .storage import DEFAULT_PATH, load_alarms, next_id, save_alarms

TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")
DAY_MAP = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
DAY_NAMES = {v: k for k, v in DAY_MAP.items()}


def validate_time(t: str) -> str:
    if not TIME_RE.match(t):
        raise argparse.ArgumentTypeError(f"Invalid time '{t}'. Use 24-hour HH:MM, e.g. 07:30")
    return t


def parse_repeat(s: str):
    if not s:
        return []
    days = []
    for part in s.split(","):
        part = part.strip().lower()
        if part not in DAY_MAP:
            raise argparse.ArgumentTypeError(
                f"Invalid day '{part}'. Use mon,tue,wed,thu,fri,sat,sun"
            )
        days.append(DAY_MAP[part])
    return sorted(set(days))


def cmd_add(args):
    alarms = load_alarms(args.file)
    alarm = Alarm(
        id=next_id(alarms),
        time=args.time,
        label=args.label or "",
        enabled=True,
        repeat=parse_repeat(args.repeat),
    )
    alarms.append(alarm)
    save_alarms(alarms, args.file)
    suffix = f" ({alarm.label})" if alarm.label else ""
    print(f"Added alarm #{alarm.id} at {alarm.time}{suffix}")


def cmd_list(args):
    alarms = load_alarms(args.file)
    if not alarms:
        print("No alarms set.")
        return
    for a in sorted(alarms, key=lambda x: x.time):
        status = "ON " if a.enabled else "OFF"
        repeat = ",".join(DAY_NAMES[i] for i in a.repeat) if a.repeat else "once"
        print(f"[{a.id}] {a.time}  {status}  repeat={repeat}  {a.label}")


def cmd_remove(args):
    alarms = load_alarms(args.file)
    remaining = [a for a in alarms if a.id != args.id]
    if len(remaining) == len(alarms):
        print(f"No alarm with id {args.id}")
        return
    save_alarms(remaining, args.file)
    print(f"Removed alarm #{args.id}")


def cmd_toggle(args):
    alarms = load_alarms(args.file)
    for a in alarms:
        if a.id == args.id:
            a.enabled = not a.enabled
            save_alarms(alarms, args.file)
            print(f"Alarm #{a.id} is now {'ON' if a.enabled else 'OFF'}")
            return
    print(f"No alarm with id {args.id}")


def cmd_run(args):
    run_loop(load_alarms, args.file)


def build_parser():
    parser = argparse.ArgumentParser(prog="alarmcli", description="A simple CLI alarm clock.")
    parser.add_argument("--file", default=DEFAULT_PATH, help="Path to alarms storage file")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a new alarm")
    p_add.add_argument("time", type=validate_time, help="Time in 24-hour HH:MM format")
    p_add.add_argument("--label", default="", help="Optional label")
    p_add.add_argument(
        "--repeat", default="", help="Comma-separated days e.g. mon,wed,fri (omit for one-time)"
    )
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List all alarms")
    p_list.set_defaults(func=cmd_list)

    p_remove = sub.add_parser("remove", help="Remove an alarm by id")
    p_remove.add_argument("id", type=int)
    p_remove.set_defaults(func=cmd_remove)

    p_toggle = sub.add_parser("toggle", help="Enable/disable an alarm by id")
    p_toggle.add_argument("id", type=int)
    p_toggle.set_defaults(func=cmd_toggle)

    p_run = sub.add_parser("run", help="Start the alarm clock (blocking, watches for triggers)")
    p_run.set_defaults(func=cmd_run)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()