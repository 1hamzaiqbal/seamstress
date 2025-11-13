
Create MVP for task management features
Nov 10
·
seamstress
·
main
·
+941
-17

Archive

Share

Create PR


Go through the readme here and attempt to create an MVP of some of the features here. Expect it to run on apple silicon macos, and work with local models and locally runnable things if possible. Try to break down each part of the plan into achieveable features, and some sort of initial visualizations as well with this.

In addition, look at this 'threads' idea that might act as a calendar based way to understand tasks. Some of these tasks can act as the example tasks (at least the ones that take time). In addition, some calendar based gui element that is able to import calendar events from my google calendar, or doing stuff with that would be nice. You can use your discretion in how to build that out and when.


Threads and ships moving toward shore. Need urgency—simulate it with 2-hour work blocks.

Seamstress board → main tracking system for threads and barges.

Major barges:

Bayesian Project

Computer Vision Project

LLM Project

Information Theory paper (treat like a paper deliverable)

Smaller barge:

Data Mining Exam 2

Threads:

Linear algebra and foundational math learning

General coursework and school responsibilities

Immediate actions:

Set up another meeting with Susy

Review papers for Raviv’s project

30-min morning and evening planning blocks to transition, plan week, and message Susy, Kevin (re: hackathon)

Prep for hackathon; check if Kevin got in

Contact Sean Thoma about potential research advising

Do two practice presentations with bullet notes and key ideas

Work on t-SNE plots (esp. MF-CLIP) and LLM project in parallel

Go over Information Theory slides daily to build fluency

Check class registration (11/11 7:30 a.m.) — figure this out over the weekend

Priority: keep Seamstress updated, run 2-hour focused sprints, and steer each barge steadily toward shore.
Copy

Version 1

Version 2

Version 3

Version 4
Summary

Implemented a modular Python package with domain models, JSON persistence, ICS ingestion, focus-state heuristics, two-hour sprint scheduling, CLI orchestration, and optional matplotlib visualization to realize the Seamstress MVP workflow locally.

Seeded demo inputs covering barges, threads, actionable tasks, focus telemetry, and calendar events, and defined the optional visualization dependency to drive the Apple Silicon–friendly MVP.

Expanded the README with feature overview, setup guidance, and workflow adaptation tips aligned with the original Seamstress brief.

Testing

✅ python -m seamstress.main --start 2024-11-07T09:00 


Files (14)

.gitignore
New

README.md
+71
-17

data/sample_calendar.ics
New

data/sample_focus_log.csv
New

data/sample_state.json
New

requirements.txt
New

seamstress/__init__.py
New

seamstress/calendar.py
New

seamstress/data_models.py
New

seamstress/focus_monitor.py
New

seamstress/main.py
New

seamstress/scheduler.py
New

seamstress/storage.py
New

seamstress/visualization.py
New



Diff
Logs

.gitignore
New
+4
-0

__pycache__/
*.pyc
outputs/
.env
README.md
+71
-17

## Project Requirements: Flow State Monitor, Time Capsule, and Project Tracking
# Seamstress MVP

### Core Objectives
This repository implements an initial minimum viable product for the Seamstress focus and planning tool described below. The MVP is designed to run locally on macOS (Apple Silicon) or any Python 3.11+ environment without cloud dependencies. It stitches together focus monitoring, time-capsule logging, project tracking, thread-based scheduling, and lightweight calendar ingestion.

* **Focus State Monitoring:**
## Features implemented

  * The system monitors your productivity using both keystrokes and optional webcam input.
  * Webcam input is supported for tasks where keyboard activity alone doesn't reflect focus levels.
- **Focus state monitoring** – ingest combined keystroke + webcam focus scores and surface break suggestions after 40+ minutes of work when productivity dips.
- **Break prompts** – detect 5–10 minute windows of low productivity and surface structured break recommendations.
- **Session capture / time capsules** – persist snapshots of recent sessions with summaries, open resources, and optional voice memo references.
- **Project-specific time tracking** – load and update JSON data describing barges (projects), associated threads, historical sessions, and cumulative time totals.
- **Thread-first planning** – map actionable tasks to 2-hour “ship toward shore” sprints with routine morning/evening planning buffers.
- **Calendar import** – parse `.ics` files exported from Google Calendar to overlay scheduled events on the day plan.
- **Visualization** – generate a horizontal Gantt-style timeline showing the planned day segmented by thread, calendar, routine, and buffer blocks.

* **Break Suggestion Logic:**
The repository ships with demo data that mirrors the “barges” and “threads” outlined in the spec:

  * The tool will prompt breaks only after a minimum of 40 minutes of work.
  * After 40 minutes, if there are 5-10 minutes of low productivity detected, it will gently suggest a break with a seamless notification, either text or voice.
- Major barges: Bayesian Project, Computer Vision Project, LLM Project, Information Theory paper.
- Smaller barge: Data Mining Exam 2.
- Threads: linear algebra refresh, coursework responsibilities, MF-CLIP analysis, hackathon preparation, daily planning routines.
- Immediate actions: meeting with Susy, reviewing Raviv’s papers, hackathon preparation, outreach, practice presentations, class registration, etc.

* **Session Capture and Replay:**
## Project Requirements (original brief)

  * The last 10 minutes of a focused work session can be recorded as a "time capsule," including open tabs, files, and a short voice memo or text summary.
  * You can explicitly choose to log the final 10 minutes when you plan to wrap up a session. This lets you mark that you're finishing in a certain timeframe and create a final log for that period.
  * When reopening a project, the tool will restore your environment and show you the summary so you can quickly resume.
> *Focus State Monitoring* – The system monitors your productivity using both keystrokes and optional webcam input. Webcam input is supported for tasks where keyboard activity alone doesn't reflect focus levels.
>
> *Break Suggestion Logic* – The tool will prompt breaks only after a minimum of 40 minutes of work. After 40 minutes, if there are 5-10 minutes of low productivity detected, it will gently suggest a break with a seamless notification, either text or voice.
>
> *Session Capture and Replay* – The last 10 minutes of a focused work session can be recorded as a "time capsule," including open tabs, files, and a short voice memo or text summary. You can explicitly choose to log the final 10 minutes when you plan to wrap up a session. When reopening a project, the tool will restore your environment and show you the summary so you can quickly resume.
>
> *Project-Specific Time Tracking* – The tool should allow you to track time spent on specific projects and maintain a running total of hours worked on each one. You can set time goals for each project (e.g., 10 hours per week) and break them into chunks (like two-hour sessions). The system will compare your actual work sessions against these estimates, providing feedback on how well you met your time estimates and goals. This can help with self-evaluation and improve your time estimation skills automatically, rather than relying on manual calendar updates.

* **Project-Specific Time Tracking:**
## Getting started

  * The tool should allow you to track time spent on specific projects and maintain a running total of hours worked on each one.
  * You can set time goals for each project (e.g., 10 hours per week) and break them into chunks (like two-hour sessions).
  * The system will compare your actual work sessions against these estimates, providing feedback on how well you met your time estimates and goals.
  * This can help with self-evaluation and improve your time estimation skills automatically, rather than relying on manual calendar updates.
1. **Create and activate a virtual environment** (recommended):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # macOS / Linux
   ```

2. **Install dependencies** (only matplotlib is required for visual output):

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the demo plan**:

   ```bash
   python -m seamstress.main --start 2024-11-07T09:00
   ```

   This will:

   - Parse the sample focus log, compute a productivity report, and display break suggestions.
   - Import the sample Google Calendar `.ics` feed and block out meetings alongside 2-hour focus sprints.
   - Summarize historical project time totals from `data/sample_state.json`.
   - Produce `outputs/daily_plan.png`, a timeline visualization of the Seamstress board for the day.

4. **Open the visualization** by viewing the generated PNG file. If you are using the repository as a template, adjust the `--state`, `--focus-log`, and `--calendar` arguments to point at your own data.

## Adapting to your workflow

- **Recording real sessions** – append new sessions (with optional time capsules) to the relevant project within the JSON file. The `storage.save_state` helper can be used from a Python REPL to persist edits cleanly.
- **Logging focus telemetry** – stream minute-level keystroke counts and webcam focus scores into the CSV layout shown in `data/sample_focus_log.csv`.
- **Threads and blocks** – reorder or modify tasks in the JSON file to determine which threads receive the next set of two-hour focus barges. The scheduler automatically adds 30-minute morning and evening planning blocks and respects existing calendar events.
- **Calendar integration** – export a Google Calendar to `.ics` (Google Calendar → Settings → Export) and pass the file path to `--calendar`. The parser handles the subset of fields needed for start/end times and summaries.
- **Apple Silicon considerations** – the only heavy dependency is matplotlib, which ships universal wheels. If you hit compilation issues, install the macOS framework build (`pip install matplotlib --no-binary=:all:`) or leverage Conda-forge.

## Next steps

This MVP focuses on local, privacy-preserving workflows. Potential follow-ups include:

- Real-time focus monitoring with keyboard hooks and webcam inference pipelines.
- GUI timeline (e.g., PyQtGraph or SwiftUI front-end) with live drag-and-drop barges.
- Bi-directional calendar sync using the Google Calendar API.
- Automatic generation of time capsules via browser/app automation and quick audio capture.
- Persistence via SQLite for richer analytics and historical trend visualizations.

Feel free to iterate by extending the data model, hooking in your own telemetry sources, or wrapping the CLI with a native macOS menu bar app.
data/sample_calendar.ics
New
+28
-0

BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Seamstress Demo//EN
BEGIN:VEVENT
UID:1@example.com
DTSTAMP:20241107T130000Z
DTSTART:20241107T140000Z
DTEND:20241107T150000Z
SUMMARY:Meeting with Susy
DESCRIPTION:Discuss next sprint planning.
END:VEVENT
BEGIN:VEVENT
UID:2@example.com
DTSTAMP:20241107T150000Z
DTSTART:20241107T160000Z
DTEND:20241107T170000Z
SUMMARY:Hackathon sync with Kevin
DESCRIPTION:Prep logistics and tasks.
END:VEVENT
BEGIN:VEVENT
UID:3@example.com
DTSTAMP:20241107T170000Z
DTSTART:20241107T180000Z
DTEND:20241107T190000Z
SUMMARY:Lecture - Information Theory
DESCRIPTION:Course session.
END:VEVENT
END:VCALENDAR
data/sample_focus_log.csv
New
+18
-0

timestamp,keystrokes,webcam_focus
2024-11-07T09:00:00,40,0.8
2024-11-07T09:05:00,55,0.7
2024-11-07T09:10:00,60,0.75
2024-11-07T09:15:00,58,0.78
2024-11-07T09:20:00,62,0.82
2024-11-07T09:25:00,65,0.80
2024-11-07T09:30:00,63,0.77
2024-11-07T09:35:00,50,0.60
2024-11-07T09:40:00,45,0.55
2024-11-07T09:45:00,20,0.45
2024-11-07T09:50:00,15,0.40
2024-11-07T09:55:00,12,0.35
2024-11-07T10:00:00,10,0.30
2024-11-07T10:05:00,55,0.75
2024-11-07T10:10:00,60,0.80
2024-11-07T10:15:00,62,0.82
2024-11-07T10:20:00,58,0.78
data/sample_state.json
New
+169
-0

{
  "projects": [
    {
      "name": "Bayesian Project",
      "weekly_goal_hours": 12,
      "description": "Ship focused on probabilistic modeling deliverables.",
      "threads": ["Work on t-SNE plots", "Review papers for Raviv’s project"],
      "sessions": [
        {
          "date": "2024-11-06",
          "duration_minutes": 110,
          "notes": "Explored MF-CLIP embeddings and prepped for new experiment.",
          "time_capsule": {
            "summary": "Pinned MF-CLIP notebook, recorded quick Loom outline, exported top plots.",
            "open_tabs": ["notebooks/mf_clip_tsne.ipynb", "docs/raviv_papers.md"],
            "voice_memo_path": null
          }
        }
      ]
    },
    {
      "name": "Computer Vision Project",
      "weekly_goal_hours": 8,
      "description": "Applied vision models sprint.",
      "threads": ["Work on t-SNE plots"],
      "sessions": []
    },
    {
      "name": "LLM Project",
      "weekly_goal_hours": 10,
      "description": "Prototype MF-CLIP alignment with LLM agents.",
      "threads": ["Work on t-SNE plots", "Prep for hackathon", "LLM Project"],
      "sessions": []
    },
    {
      "name": "Information Theory paper",
      "weekly_goal_hours": 6,
      "description": "Treat like paper deliverable; daily review of slides.",
      "threads": ["Go over Information Theory slides daily"],
      "sessions": []
    },
    {
      "name": "Data Mining Exam 2",
      "weekly_goal_hours": 4,
      "description": "Smaller barge focused on exam prep.",
      "threads": ["General coursework and school responsibilities"],
      "sessions": []
    }
  ],
  "threads": [
    {
      "name": "Linear algebra and foundational math learning",
      "cadence_minutes": 120,
      "notes": "Daily review block with spaced repetition prompts."
    },
    {
      "name": "General coursework and school responsibilities",
      "cadence_minutes": 90,
      "notes": "Includes registration checks, exam prep, and admin."
    },
    {
      "name": "Work on t-SNE plots",
      "cadence_minutes": 120,
      "notes": "Focus blocks for MF-CLIP visualization and analysis."
    },
    {
      "name": "Prep for hackathon",
      "cadence_minutes": 120,
      "notes": "Coordinate with Kevin, draft pitches, rehearse presentations."
    },
    {
      "name": "30-min planning",
      "cadence_minutes": 30,
      "notes": "Morning and evening context switching rituals."
    },
    {
      "name": "LLM Project",
      "cadence_minutes": 120,
      "notes": "Deep work exploring LLM alignment experiments."
    },
    {
      "name": "Go over Information Theory slides daily",
      "cadence_minutes": 60,
      "notes": "Short daily fluency reps on course material."
    }
  ],
  "tasks": [
    {
      "title": "Set up another meeting with Susy",
      "estimated_minutes": 30,
      "thread": "General coursework and school responsibilities",
      "status": "pending",
      "tags": ["immediate"],
      "deadline": "2024-11-08"
    },
    {
      "title": "Review papers for Raviv’s project",
      "estimated_minutes": 120,
      "thread": "Work on t-SNE plots",
      "status": "pending",
      "tags": ["immediate"],
      "deadline": "2024-11-09"
    },
    {
      "title": "Morning planning block",
      "estimated_minutes": 30,
      "thread": "30-min planning",
      "status": "routine",
      "tags": ["daily"],
      "deadline": null
    },
    {
      "title": "Evening planning block",
      "estimated_minutes": 30,
      "thread": "30-min planning",
      "status": "routine",
      "tags": ["daily"],
      "deadline": null
    },
    {
      "title": "Prep for hackathon; check if Kevin got in",
      "estimated_minutes": 120,
      "thread": "Prep for hackathon",
      "status": "pending",
      "tags": ["hackathon"],
      "deadline": "2024-11-10"
    },
    {
      "title": "Contact Sean Thoma about potential research advising",
      "estimated_minutes": 30,
      "thread": "General coursework and school responsibilities",
      "status": "pending",
      "tags": ["outreach"],
      "deadline": "2024-11-09"
    },
    {
      "title": "Do two practice presentations with bullet notes",
      "estimated_minutes": 120,
      "thread": "Prep for hackathon",
      "status": "pending",
      "tags": ["presentation"],
      "deadline": "2024-11-11"
    },
    {
      "title": "Work on t-SNE plots (MF-CLIP)",
      "estimated_minutes": 120,
      "thread": "Work on t-SNE plots",
      "status": "pending",
      "tags": ["analysis"],
      "deadline": "2024-11-08"
    },
    {
      "title": "LLM project sprint",
      "estimated_minutes": 120,
      "thread": "LLM Project",
      "status": "pending",
      "tags": ["research"],
      "deadline": "2024-11-09"
    },
    {
      "title": "Check class registration (11/11 7:30 a.m.)",
      "estimated_minutes": 45,
      "thread": "General coursework and school responsibilities",
      "status": "pending",
      "tags": ["admin"],
      "deadline": "2024-11-09"
    }
  ]
}
requirements.txt
New
+1
-0

matplotlib>=3.8
seamstress/__init__.py
New
+11
-0

"""Seamstress MVP package."""

from importlib.metadata import version

__all__ = ["__version__"]


try:
    __version__ = version("seamstress")
except Exception:  # pragma: no cover - version metadata absent in editable installs
    __version__ = "0.1.0"
seamstress/calendar.py
New
+46
-0

"""Minimal ICS parser for importing calendar events."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from .data_models import CalendarEvent


def _parse_datetime(value: str) -> datetime:
    if value.endswith("Z"):
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ")
    if len(value) == 8:
        return datetime.strptime(value, "%Y%m%d")
    return datetime.strptime(value, "%Y%m%dT%H%M%S")


def load_events(path: Path) -> List[CalendarEvent]:
    """Parse a subset of ICS into calendar events."""

    lines = [line.strip() for line in Path(path).read_text().splitlines()]
    events: List[CalendarEvent] = []
    cursor = 0
    while cursor < len(lines):
        if lines[cursor] == "BEGIN:VEVENT":
            cursor += 1
            payload = {}
            while cursor < len(lines) and lines[cursor] != "END:VEVENT":
                line = lines[cursor]
                if ":" in line:
                    key, value = line.split(":", 1)
                    payload[key] = value
                cursor += 1
            events.append(
                CalendarEvent(
                    uid=payload.get("UID", ""),
                    start=_parse_datetime(payload.get("DTSTART", "")),
                    end=_parse_datetime(payload.get("DTEND", "")),
                    summary=payload.get("SUMMARY", ""),
                    description=payload.get("DESCRIPTION", ""),
                )
            )
        cursor += 1
    return events
seamstress/data_models.py
New
+77
-0

"""Core data models for the Seamstress MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass(slots=True)
class TimeCapsule:
    """Captures the final snapshot of a focus session."""

    summary: str
    open_tabs: List[str]
    voice_memo_path: Optional[str] = None


@dataclass(slots=True)
class Session:
    """Represents a recorded work session."""

    date: datetime
    duration_minutes: int
    notes: str = ""
    time_capsule: Optional[TimeCapsule] = None


@dataclass(slots=True)
class Project:
    """High-level deliverable ("barge") tracked by the system."""

    name: str
    weekly_goal_hours: float
    description: str
    threads: List[str] = field(default_factory=list)
    sessions: List[Session] = field(default_factory=list)

    @property
    def total_minutes(self) -> int:
        return sum(session.duration_minutes for session in self.sessions)


@dataclass(slots=True)
class Thread:
    """Thread represents a stream of work that can cut across projects."""

    name: str
    cadence_minutes: int
    notes: str = ""


@dataclass(slots=True)
class Task:
    """Actionable item associated with a thread."""

    title: str
    estimated_minutes: int
    thread: str
    status: str
    tags: List[str] = field(default_factory=list)
    deadline: Optional[datetime] = None


@dataclass(slots=True)
class CalendarEvent:
    """Simplified representation of calendar events imported from an ICS file."""

    uid: str
    start: datetime
    end: datetime
    summary: str
    description: str = ""

    @property
    def duration_minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)
seamstress/focus_monitor.py
New
+107
-0

"""Focus state monitoring and break suggestion heuristics."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List


@dataclass(slots=True)
class FocusSample:
    timestamp: datetime
    keystrokes: int
    webcam_focus: float

    @property
    def productivity_score(self) -> float:
        """Heuristic score combining keystrokes and webcam focus."""

        normalized_keys = min(self.keystrokes / 60, 1.0)
        return 0.7 * normalized_keys + 0.3 * self.webcam_focus


@dataclass(slots=True)
class BreakSuggestion:
    start: datetime
    end: datetime
    reason: str


@dataclass(slots=True)
class FocusReport:
    samples: List[FocusSample]
    break_suggestions: List[BreakSuggestion]

    @property
    def total_minutes(self) -> int:
        if not self.samples:
            return 0
        span = self.samples[-1].timestamp - self.samples[0].timestamp
        return int(span.total_seconds() // 60)


class FocusMonitor:
    """Implements a minimal focus heuristic for the MVP."""

    def __init__(
        self,
        sustained_minutes: int = 40,
        low_productivity_threshold: float = 0.45,
        low_productivity_minutes: int = 8,
    ) -> None:
        self.sustained_minutes = sustained_minutes
        self.low_productivity_threshold = low_productivity_threshold
        self.low_productivity_minutes = low_productivity_minutes

    def parse_csv(self, path: Path) -> List[FocusSample]:
        samples: List[FocusSample] = []
        with Path(path).open() as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                samples.append(
                    FocusSample(
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                        keystrokes=int(row["keystrokes"]),
                        webcam_focus=float(row["webcam_focus"]),
                    )
                )
        return samples

    def analyze(self, samples: Iterable[FocusSample]) -> FocusReport:
        sample_list = list(samples)
        break_suggestions: List[BreakSuggestion] = []
        if not sample_list:
            return FocusReport(samples=[], break_suggestions=[])

        window: List[FocusSample] = []
        session_start = sample_list[0].timestamp

        for sample in sample_list:
            window.append(sample)
            threshold = timedelta(minutes=self.low_productivity_minutes)
            while len(window) > 1 and (sample.timestamp - window[0].timestamp) >= threshold:
                window.pop(0)

            session_duration = (sample.timestamp - session_start).total_seconds() / 60

            if session_duration >= self.sustained_minutes and window:
                avg_productivity = sum(s.productivity_score for s in window) / len(window)
                if avg_productivity < self.low_productivity_threshold:
                    break_suggestions.append(
                        BreakSuggestion(
                            start=window[0].timestamp,
                            end=sample.timestamp,
                            reason=(
                                "Focus has dipped for the last "
                                f"{self.low_productivity_minutes} minutes."
                            ),
                        )
                    )
                    session_start = sample.timestamp
                    window.clear()
                    window.append(sample)

        return FocusReport(samples=sample_list, break_suggestions=break_suggestions)
seamstress/main.py
New
+89
-0

"""Command-line entry point for the Seamstress MVP demo."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
from pathlib import Path

from . import __version__
from .calendar import load_events
from .focus_monitor import FocusMonitor
from .scheduler import DailyScheduler
from .storage import load_state
from .visualization import plot_daily_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Seamstress MVP demo plan.")
    parser.add_argument("--state", type=Path, default=Path("data/sample_state.json"))
    parser.add_argument(
        "--focus-log", type=Path, default=Path("data/sample_focus_log.csv")
    )
    parser.add_argument(
        "--calendar", type=Path, default=Path("data/sample_calendar.ics")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("outputs/daily_plan.png"),
        help="Where to save the generated visualization.",
    )
    parser.add_argument(
        "--start", type=str, default=datetime.now().strftime("%Y-%m-%dT09:00"),
        help="Day start timestamp (local time).",
    )
    parser.add_argument(
        "--focus-blocks", type=int, default=3, help="Number of 2-hour focus blocks."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    projects, threads, tasks = load_state(args.state)
    focus_monitor = FocusMonitor()
    samples = focus_monitor.parse_csv(args.focus_log)
    report = focus_monitor.analyze(samples)

    calendar_events = load_events(args.calendar)
    start_time = datetime.fromisoformat(args.start)
    scheduler = DailyScheduler(day_start=start_time, focus_blocks=args.focus_blocks)
    plan = scheduler.build_plan(tasks=tasks, events=calendar_events)

    plot_path = None
    try:
        plot_path = plot_daily_plan(plan, args.output)
    except RuntimeError as exc:
        print(f"Visualization skipped: {exc}")

    print(f"Seamstress v{__version__}")
    print("=" * 40)
    print(f"Loaded {len(projects)} projects, {len(threads)} threads, {len(tasks)} tasks.")
    print(f"Focus session length: {report.total_minutes} minutes")
    if report.break_suggestions:
        print("\nBreak suggestions:")
        for suggestion in report.break_suggestions:
            print(
                f"  {suggestion.start.strftime('%H:%M')}–{suggestion.end.strftime('%H:%M')}: {suggestion.reason}"
            )
    else:
        print("No break suggestions triggered.")

    thread_summary = scheduler.summarize_by_thread(plan)
    print("\nPlanned focus blocks by thread:")
    for thread, minutes in thread_summary.items():
        print(f"  {thread}: {minutes // 60}h {minutes % 60:02d}m")

    project_totals = Counter()
    for project in projects:
        project_totals[project.name] += project.total_minutes
    print("\nHistorical project time totals:")
    for project, minutes in project_totals.items():
        print(f"  {project}: {minutes // 60}h {minutes % 60:02d}m recorded")

    if plot_path:
        print(f"\nVisualization saved to: {plot_path}")


if __name__ == "__main__":  # pragma: no cover
    main()
seamstress/scheduler.py
New
+106
-0

"""Daily scheduling and thread orchestration."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Sequence

from .data_models import CalendarEvent, Task

BLOCK_MINUTES = 120
PLANNING_BLOCK_MINUTES = 30


@dataclass(slots=True)
class ScheduledBlock:
    """Represents either a work sprint or imported calendar event."""

    start: datetime
    end: datetime
    label: str
    source: str

    @property
    def duration_minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)


@dataclass(slots=True)
class DailyPlan:
    date: datetime
    blocks: List[ScheduledBlock]

    @property
    def total_work_minutes(self) -> int:
        return sum(block.duration_minutes for block in self.blocks if block.source == "thread")


class DailyScheduler:
    """Generates a plan that balances threads and calendar events."""

    def __init__(self, day_start: datetime, focus_blocks: int = 3) -> None:
        self.day_start = day_start
        self.focus_blocks = focus_blocks

    def build_plan(
        self,
        tasks: Sequence[Task],
        events: Iterable[CalendarEvent],
        timezone_offset_hours: int = -5,
    ) -> DailyPlan:
        blocks: List[ScheduledBlock] = []
        current = self.day_start

        sorted_events = sorted(events, key=lambda event: event.start)
        event_iter = iter(sorted_events)
        next_event = next(event_iter, None)

        def add_block(end: datetime, label: str, source: str) -> None:
            blocks.append(ScheduledBlock(start=current, end=end, label=label, source=source))

        def align_to_event(start: datetime, event: CalendarEvent) -> datetime:
            event_start = event.start + timedelta(hours=timezone_offset_hours)
            return max(start, event_start)

        task_queue = [task for task in tasks if task.status != "routine"]
        block_index = 0

        while block_index < self.focus_blocks and task_queue:
            if block_index == 0:
                end = current + timedelta(minutes=PLANNING_BLOCK_MINUTES)
                add_block(end, "Morning planning", "routine")
                current = end

            block_task = task_queue.pop(0)
            end = current + timedelta(minutes=BLOCK_MINUTES)
            add_block(end, f"{block_task.thread}: {block_task.title}", "thread")
            current = end
            block_index += 1

            while next_event:
                local_start = align_to_event(current, next_event)
                local_end = next_event.end + timedelta(hours=timezone_offset_hours)
                if local_start < local_end and current <= local_start < current + timedelta(hours=4):
                    if current < local_start:
                        add_block(local_start, "Buffer / transit", "buffer")
                        current = local_start
                    add_block(local_end, next_event.summary, "calendar")
                    current = local_end
                    next_event = next(event_iter, None)
                else:
                    break

        end = current + timedelta(minutes=PLANNING_BLOCK_MINUTES)
        add_block(end, "Evening planning", "routine")

        return DailyPlan(date=self.day_start, blocks=blocks)

    def summarize_by_thread(self, plan: DailyPlan) -> Dict[str, int]:
        summary: Dict[str, int] = defaultdict(int)
        for block in plan.blocks:
            if block.source == "thread":
                thread_name = block.label.split(":", maxsplit=1)[0]
                summary[thread_name] += block.duration_minutes
        return dict(summary)
seamstress/storage.py
New
+129
-0

"""Lightweight JSON storage helpers."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from .data_models import CalendarEvent, Project, Session, Task, Thread, TimeCapsule

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


def _parse_time_capsule(raw: Dict) -> TimeCapsule:
    return TimeCapsule(
        summary=raw["summary"],
        open_tabs=list(raw.get("open_tabs", [])),
        voice_memo_path=raw.get("voice_memo_path"),
    )


def _parse_session(raw: Dict) -> Session:
    capsule = raw.get("time_capsule")
    return Session(
        date=datetime.strptime(raw["date"], DATE_FORMAT),
        duration_minutes=int(raw["duration_minutes"]),
        notes=raw.get("notes", ""),
        time_capsule=_parse_time_capsule(capsule) if capsule else None,
    )


def _parse_project(raw: Dict) -> Project:
    return Project(
        name=raw["name"],
        weekly_goal_hours=float(raw.get("weekly_goal_hours", 0)),
        description=raw.get("description", ""),
        threads=list(raw.get("threads", [])),
        sessions=[_parse_session(session) for session in raw.get("sessions", [])],
    )


def _parse_thread(raw: Dict) -> Thread:
    return Thread(
        name=raw["name"],
        cadence_minutes=int(raw.get("cadence_minutes", 0)),
        notes=raw.get("notes", ""),
    )


def _parse_task(raw: Dict) -> Task:
    deadline = raw.get("deadline")
    parsed_deadline = (
        datetime.strptime(deadline, DATE_FORMAT) if deadline else None
    )
    return Task(
        title=raw["title"],
        estimated_minutes=int(raw.get("estimated_minutes", 0)),
        thread=raw.get("thread", ""),
        status=raw.get("status", "pending"),
        tags=list(raw.get("tags", [])),
        deadline=parsed_deadline,
    )


def load_state(path: Path) -> Tuple[List[Project], List[Thread], List[Task]]:
    """Load persisted state from JSON."""

    payload = json.loads(Path(path).read_text())
    projects = [_parse_project(raw) for raw in payload.get("projects", [])]
    threads = [_parse_thread(raw) for raw in payload.get("threads", [])]
    tasks = [_parse_task(raw) for raw in payload.get("tasks", [])]
    return projects, threads, tasks


def save_state(
    path: Path, projects: List[Project], threads: List[Thread], tasks: List[Task]
) -> None:
    """Persist state to JSON."""

    payload = {
        "projects": [
            {
                "name": project.name,
                "weekly_goal_hours": project.weekly_goal_hours,
                "description": project.description,
                "threads": list(project.threads),
                "sessions": [
                    {
                        "date": session.date.strftime(DATE_FORMAT),
                        "duration_minutes": session.duration_minutes,
                        "notes": session.notes,
                        "time_capsule": asdict(session.time_capsule)
                        if session.time_capsule
                        else None,
                    }
                    for session in project.sessions
                ],
            }
            for project in projects
        ],
        "threads": [asdict(thread) for thread in threads],
        "tasks": [
            {
                "title": task.title,
                "estimated_minutes": task.estimated_minutes,
                "thread": task.thread,
                "status": task.status,
                "tags": list(task.tags),
                "deadline": task.deadline.strftime(DATE_FORMAT)
                if task.deadline
                else None,
            }
            for task in tasks
        ],
    }
    Path(path).write_text(json.dumps(payload, indent=2))


def serialize_calendar_event(event: CalendarEvent) -> Dict:
    return {
        "uid": event.uid,
        "start": event.start.strftime(ISO_FORMAT),
        "end": event.end.strftime(ISO_FORMAT),
        "summary": event.summary,
        "description": event.description,
    }
seamstress/visualization.py
New
+85
-0

"""Visualization utilities for Seamstress."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Dict

from .scheduler import DailyPlan

COLORS = {
    "thread": "#4C72B0",
    "routine": "#55A868",
    "calendar": "#C44E52",
    "buffer": "#8172B3",
}


def plot_daily_plan(plan: DailyPlan, output_path: Path) -> Path:
    """Create a horizontal timeline of the daily plan."""

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - depends on optional dep
        raise RuntimeError(
            "matplotlib is required for visualization. Install it with 'pip install -r requirements.txt'."
        ) from exc

    if not plan.blocks:
        raise ValueError("Daily plan has no blocks to plot")

    fig, ax = plt.subplots(figsize=(10, 3))
    start_base = plan.blocks[0].start

    for block in plan.blocks:
        start_delta = (block.start - start_base).total_seconds() / 3600
        duration = block.duration_minutes / 60
        color = COLORS.get(block.source, "#CCB974")
        ax.barh(
            y=[0],
            width=duration,
            left=start_delta,
            height=0.4,
            color=color,
            edgecolor="black",
        )
        ax.text(
            start_delta + duration / 2,
            0,
            block.label,
            ha="center",
            va="center",
            fontsize=8,
            color="white" if block.source != "routine" else "black",
        )

    ax.set_xlabel("Hours from day start")
    ax.set_yticks([])
    ax.set_title(plan.date.strftime("Seamstress focus sprints"))
    ax.set_xlim(
        0,
        max((block.end - start_base).total_seconds() / 3600 for block in plan.blocks)
        + 0.5,
    )

    legend_handles = [
        plt.Line2D([0], [0], color=color, lw=4, label=label.title())
        for label, color in COLORS.items()
    ]
    ax.legend(handles=legend_handles, loc="lower right")
    fig.tight_layout()

    output_path = Path(output_path)
    fig.savefig(output_path)
    plt.close(fig)
    return output_path


def visualize_thread_allocation(plan: DailyPlan) -> Dict[str, int]:
    summary: Dict[str, int] = defaultdict(int)
    for block in plan.blocks:
        if block.source == "thread":
            thread_name = block.label.split(":", maxsplit=1)[0]
            summary[thread_name] += block.duration_minutes
    return dict(summary)
