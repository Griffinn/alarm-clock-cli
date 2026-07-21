# alarmcli — A CLI Alarm Clock

A simple, dependency-free command-line alarm clock written in Python. Set alarms,
list them, toggle them on/off, and run a foreground clock that fires alarms at
the right time with a sound and a dismiss/snooze prompt.

No web UI, no database — alarms persist to a small JSON file on disk.

## Features

- Add one-time or repeating (specific weekday) alarms
- List, toggle on/off, and remove alarms
- Foreground `run` command that watches the clock and fires alarms
- Dismiss or snooze (5 min) when an alarm goes off
- Cross-platform beep (terminal bell on Mac/Linux, `winsound` on Windows)
- Zero runtime dependencies — pure Python standard library
- Unit tests for the storage and validation logic

## Requirements

- Python 3.8+
- (Optional, for running tests) `pytest`

## Setup

```bash
git clone <this-repo-url>
cd alarm-clock-cli
python -m pip install pytest   # optional, only needed to run tests
```

No other installation step — the app itself has no third-party dependencies.

## Usage

```bash
# Add a one-time alarm
python -m alarmcli.cli add 07:30 --label "Wake up"

# Add a repeating alarm (Mon/Wed/Fri)
python -m alarmcli.cli add 06:00 --label "Gym" --repeat mon,wed,fri

# List all alarms
python -m alarmcli.cli list

# Turn an alarm off/on without deleting it (use the id shown in `list`)
python -m alarmcli.cli toggle 1

# Delete an alarm
python -m alarmcli.cli remove 1

# Start the alarm clock (blocking — this is what actually "runs" the clock)
python -m alarmcli.cli run
```

On Windows, use `python` (not `python3`) unless you've specifically set up a
`python3` alias.

Every command also accepts an optional `--file <path>` to point at a different
alarms JSON file, e.g. for testing:

```bash
python -m alarmcli.cli --file test_alarms.json add 09:00
```

### When an alarm fires

1. The terminal prints `⏰ ALARM: <label> (<time>)`
2. It beeps 3 times
3. It waits for you to type:
   - **Enter** → dismiss (one-time alarms auto-disable after dismissal)
   - **s** + Enter → snooze 5 minutes

## Running tests

```bash
python -m pytest tests/ -v
```

Covers: alarm serialization round-trip, save/load from disk, ID generation,
day-of-week parsing, and time-format validation.

## Design decisions

- **One-shot CLI commands, not a REPL.** `add`/`list`/`remove`/`toggle` are
  quick management commands; `run` is the long-lived process that actually
  watches the clock. This keeps alarm management separate from "the clock
  being on," which felt more honest than faking a background daemon in a
  time-boxed CLI tool.
- **JSON file over a database.** The brief explicitly ruled out a database,
  and a JSON file is simple, human-readable, and easy to inspect/debug during
  development.
- **Foreground blocking process, not a system daemon.** Turning this into a
  systemd/launchd background service was out of scope for the time available
  and adds OS-specific complexity that doesn't reflect the core problem being
  solved.
- **Check time once per real minute, not on every poll.** The loop polls
  every second but only evaluates alarms when the wall-clock minute changes,
  so an alarm fires exactly once per due minute instead of repeatedly during
  the ~60 seconds it's active.

## Known limitations / what I'd add with more time

- **Same-day re-fire ambiguity:** a one-time alarm only stores `HH:MM`, not a
  full date. If the `run` process is left going past midnight, a one-time
  alarm you missed today could fire again tomorrow. Fixing this properly means
  storing a "last triggered" date and comparing against it — noted here
  rather than fixed, given the time box for this exercise.
- **Single alarm ringing at a time:** while an alarm is waiting for
  dismiss/snooze input, the loop is blocked and won't check for other alarms.
  Fine for personal use; wouldn't scale to many simultaneous alarms.
- **No audio file support** — uses the terminal bell / `winsound.Beep` rather
  than playing a sound file, to keep the dependency list at zero.
- **No timezone/DST handling** beyond whatever the host system's local clock
  reports.
- Possible next features: custom snooze duration, alarm editing (vs.
  delete+recreate), colorized output, a `--quiet` mode for tests.

## Project structure

```
alarm-clock-cli/
├── alarmcli/
│   ├── __init__.py
│   ├── cli.py          # argparse entrypoint / subcommands
│   ├── models.py        # Alarm dataclass
│   ├── storage.py       # JSON load/save
│   └── scheduler.py     # the run loop + trigger/beep logic
├── tests/
│   └── test_alarm.py
├── requirements.txt
└── README.md
```