"""The blocking loop that watches the clock and fires alarms."""
import platform
import sys
import time as time_module
from datetime import datetime
from typing import List

from .models import Alarm
from .storage import save_alarms

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    import winsound


def beep(times: int = 3) -> None:
    for _ in range(times):
        if IS_WINDOWS:
            # Terminal bell (\a) is unreliable on Windows consoles, so use
            # winsound to guarantee an audible tone instead.
            winsound.Beep(1000, 400)  # 1000 Hz for 400 ms
        else:
            sys.stdout.write("\a")
            sys.stdout.flush()
        time_module.sleep(0.3)


def _add_minutes(hhmm: str, minutes: int) -> str:
    h, m = map(int, hhmm.split(":"))
    total = (h * 60 + m + minutes) % (24 * 60)
    return f"{total // 60:02d}:{total % 60:02d}"


def handle_trigger(alarm: Alarm, alarms: List[Alarm], path: str) -> None:
    print(f"\n\u23f0 ALARM: {alarm.label or 'Alarm'} ({alarm.time})")
    beep()
    while True:
        choice = input("[Enter]=dismiss, 's'+Enter=snooze 5 min: ").strip().lower()
        if choice == "s":
            alarm.time = _add_minutes(alarm.time, 5)
            print(f"Snoozed until {alarm.time}")
            save_alarms(alarms, path)
            return
        if not alarm.repeat:
            alarm.enabled = False
        print("Dismissed.")
        save_alarms(alarms, path)
        return


def run_loop(load_fn, path: str, poll_interval: float = 1.0) -> None:
    print("Alarm clock running. Press Ctrl+C to stop.")
    last_minute = None
    try:
        while True:
            now = datetime.now()
            current_hm = now.strftime("%H:%M")
            if current_hm != last_minute:
                last_minute = current_hm
                alarms = load_fn(path)
                weekday = now.weekday()
                for alarm in alarms:
                    if not alarm.enabled or alarm.time != current_hm:
                        continue
                    if alarm.repeat and weekday not in alarm.repeat:
                        continue
                    handle_trigger(alarm, alarms, path)
            time_module.sleep(poll_interval)
    except KeyboardInterrupt:
        print("\nAlarm clock stopped.")