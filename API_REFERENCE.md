# Seamstress API Reference

This document covers the Python API for programmatic use of Seamstress components.

---

## Data Models (`seamstress.data_models`)

### WorkBlock

Represents a contiguous period of focused work.

```python
@dataclass
class WorkBlock:
    start: datetime
    end: datetime
    project: str
    focus_score: float
    
    @property
    def duration(self) -> timedelta
```

**Example:**
```python
from datetime import datetime
from seamstress.data_models import WorkBlock

block = WorkBlock(
    start=datetime(2025, 11, 13, 10, 0),
    end=datetime(2025, 11, 13, 12, 0),
    project="Bayesian Project",
    focus_score=0.82
)
print(block.duration)  # 2:00:00
```

---

### ProjectGoal

Configuration for time investment targets per project.

```python
@dataclass
class ProjectGoal:
    project: str
    weekly_target_hours: float
    block_minutes: int = 120
    
    def block_count_for_week(self) -> float
```

**Example:**
```python
from seamstress.data_models import ProjectGoal

goal = ProjectGoal(
    project="LLM Project",
    weekly_target_hours=10,
    block_minutes=120
)
print(goal.block_count_for_week())  # 5.0
```

---

### TimeCapsule

Snapshot of work session end state.

```python
@dataclass
class TimeCapsule:
    project: str
    created_at: datetime
    summary: str
    open_resources: List[str] = field(default_factory=list)
    memo_path: Optional[Path] = None
```

**Example:**
```python
from datetime import datetime
from seamstress.data_models import TimeCapsule

capsule = TimeCapsule(
    project="Computer Vision Project",
    created_at=datetime.now(),
    summary="Completed t-SNE analysis",
    open_resources=[
        "notebooks/tsne.ipynb",
        "https://arxiv.org/abs/1803.08494"
    ],
    memo_path=Path("notes/session_2024_11_13.md")
)
```

---

### Thread

Individual work stream within a barge.

```python
@dataclass
class Thread:
    name: str
    description: str
    urgency_level: int
    related_projects: List[str] = field(default_factory=list)
    tasks: List[str] = field(default_factory=list)
```

**Urgency Levels:**
- 1: Low urgency
- 2: Medium urgency  
- 3: High urgency (🔥🔥🔥)

---

### Barge

Collection of related threads heading toward a deadline.

```python
@dataclass
class Barge:
    name: str
    description: str
    expected_landfall: Optional[datetime] = None
    threads: List[Thread] = field(default_factory=list)
```

---

### SeamstressState

Root state object persisted to JSON.

```python
@dataclass
class SeamstressState:
    projects: Dict[str, ProjectGoal] = field(default_factory=dict)
    work_blocks: List[WorkBlock] = field(default_factory=list)
    time_capsules: List[TimeCapsule] = field(default_factory=list)
    barges: List[Barge] = field(default_factory=list)
    
    def add_work_block(self, block: WorkBlock) -> None
    def add_time_capsule(self, capsule: TimeCapsule) -> None
    def register_project_goal(self, goal: ProjectGoal) -> None
    def upsert_barge(self, barge: Barge) -> None
    def iter_threads(self) -> Iterable[Thread]
```

---

## Storage (`seamstress.storage`)

### Core Functions

#### load_state()

```python
def load_state() -> SeamstressState
```

Loads the current state from `~/.seamstress/state.json`.

**Returns:** `SeamstressState` object

**Example:**
```python
from seamstress.storage import load_state

state = load_state()
print(f"Projects: {len(state.projects)}")
print(f"Work blocks: {len(state.work_blocks)}")
```

---

#### save_state()

```python
def save_state(state: SeamstressState) -> None
```

Persists state to `~/.seamstress/state.json` with backup.

**Side Effects:** Creates `state.json.bak` backup

**Example:**
```python
from seamstress.storage import load_state, save_state
from seamstress.data_models import WorkBlock
from datetime import datetime

state = load_state()
block = WorkBlock(
    start=datetime(2025, 11, 13, 14, 0),
    end=datetime(2025, 11, 13, 16, 0),
    project="LLM Project",
    focus_score=0.88
)
state.add_work_block(block)
save_state(state)
```

---

#### iter_work_blocks()

```python
def iter_work_blocks(state: SeamstressState) -> Iterable[WorkBlock]
```

Generator for work blocks with optional filtering.

**Example:**
```python
from seamstress.storage import load_state, iter_work_blocks
from datetime import datetime, timedelta

state = load_state()
now = datetime.utcnow()
week_ago = now - timedelta(days=7)

recent_blocks = [
    block for block in iter_work_blocks(state)
    if block.start >= week_ago
]
```

---

## Calendar Integration (`seamstress.calendar_ics`)

### IcsEvent

```python
@dataclass
class IcsEvent:
    summary: str
    start: datetime
    end: datetime
    location: str = ""
    uid: str = ""
```

---

### import_ics()

```python
def import_ics(path: Path) -> List[IcsEvent]
```

Parses ICS file, with fallback if `ics` library unavailable.

**Returns:** Sorted list of events

**Example:**
```python
from pathlib import Path
from seamstress.calendar_ics import import_ics

events = import_ics(Path("~/Downloads/calendar.ics").expanduser())
for event in events:
    print(f"{event.summary} at {event.start}")
```

---

## Focus Analysis (`seamstress.focus_offline`)

### Sample

```python
@dataclass
class Sample:
    t: datetime
    keys: int
    webcam: float
    
    @property
    def score(self) -> float
```

**Score Calculation:** `0.7 * min(keys/60, 1.0) + 0.3 * webcam`

---

### BreakHint

```python
@dataclass
class BreakHint:
    start: datetime
    end: datetime
    reason: str
```

---

### load_csv()

```python
def load_csv(path: Path) -> List[Sample]
```

Loads focus metrics from CSV.

**Expected Columns:**
- `timestamp` (ISO 8601 format)
- `keystrokes` (integer)
- `webcam_focus` (float 0.0-1.0)

**Example:**
```python
from pathlib import Path
from seamstress.focus_offline import load_csv

samples = load_csv(Path("data/samples/focus.csv"))
print(f"Loaded {len(samples)} samples")
```

---

### analyze()

```python
def analyze(
    samples: List[Sample],
    sustained_min: int = 40,
    low_win_min: int = 8,
    thresh: float = 0.45,
) -> List[BreakHint]
```

Identifies low-focus windows suggesting break times.

**Parameters:**
- `sustained_min`: Minutes of work before considering breaks
- `low_win_min`: Window size for low-focus detection
- `thresh`: Focus score threshold (0.0-1.0)

**Example:**
```python
from seamstress.focus_offline import load_csv, analyze

samples = load_csv(Path("focus_data.csv"))
hints = analyze(samples, sustained_min=45, thresh=0.5)
for hint in hints:
    print(f"Break suggested: {hint.start} - {hint.reason}")
```

---

## Schedule Building (`seamstress.schedule_daily`)

### Block

```python
@dataclass
class Block:
    start: datetime
    end: datetime
    label: str
    source: str
```

**Source Values:**
- `"ritual"` - Morning/evening planning
- `"sprint"` - 2-hour focus block
- `"event"` - Calendar event
- `"buffer"` - Transit/setup time

---

### build_simple_schedule()

```python
def build_simple_schedule(
    day_start: datetime,
    projects: Iterable[str],
    events: Iterable[Tuple[datetime, datetime, str]],
    focus_blocks: int = 3,
) -> List[Block]
```

Creates a daily schedule with rituals, sprints, and calendar events.

**Example:**
```python
from datetime import datetime
from seamstress.schedule_daily import build_simple_schedule

start = datetime(2025, 11, 13, 9, 0)
projects = ["Bayesian Project", "LLM Project", "Computer Vision"]
events = [
    (datetime(2025, 11, 13, 14, 0), datetime(2025, 11, 13, 15, 0), "Team Meeting")
]

schedule = build_simple_schedule(start, projects, events, focus_blocks=3)
for block in schedule:
    print(f"{block.start:%H:%M} - {block.label}")
```

---

## Time Capsules (`seamstress.timecapsule`)

### Probe

```python
@dataclass
class Probe:
    description: str
    command: List[str]
```

Represents a macOS context capture command (AppleScript).

---

### create_time_capsule()

```python
def create_time_capsule(
    project: str,
    summary: str,
    resources: Iterable[str] = (),
    include_probes: bool = True,
) -> TimeCapsule
```

Creates and persists a time capsule with optional context probes.

**Probes (macOS only):**
- Safari open tabs
- VSCode workspace folders

**Example:**
```python
from seamstress.timecapsule import create_time_capsule

capsule = create_time_capsule(
    project="Information Theory Paper",
    summary="Completed draft of section 3",
    resources=[
        "papers/info_theory_draft.pdf",
        "https://en.wikipedia.org/wiki/Shannon_entropy"
    ],
    include_probes=True  # Captures Safari tabs, VSCode state
)
print(f"Capsule created at {capsule.created_at}")
```

---

## Visualization (`seamstress.visualization`)

### work_blocks_to_dataframe()

```python
def work_blocks_to_dataframe(blocks: Iterable[WorkBlock]) -> pd.DataFrame
```

Converts work blocks to pandas DataFrame for analysis.

**Columns:**
- `project`
- `start` (datetime)
- `end` (datetime)
- `duration_hours` (float)
- `focus_score` (float)

**Example:**
```python
from seamstress.storage import load_state, iter_work_blocks
from seamstress.visualization import work_blocks_to_dataframe

state = load_state()
df = work_blocks_to_dataframe(iter_work_blocks(state))
print(df.groupby('project')['duration_hours'].sum())
```

---

### plot_weekly_blocks()

```python
def plot_weekly_blocks(output_path: Path) -> Path
```

Generates stacked bar chart of last 7 days' focus.

**Returns:** Path to saved PNG

**Example:**
```python
from pathlib import Path
from seamstress.visualization import plot_weekly_blocks

output = plot_weekly_blocks(Path("artifacts/my_week.png"))
print(f"Chart saved to {output}")
```

---

### generate_two_hour_block_plan()

```python
def generate_two_hour_block_plan(projects: List[str], days: int = 5) -> pd.DataFrame
```

Creates round-robin 2-hour sprint plan.

**Returns:** DataFrame with columns: `day`, `start`, `end`, `project`

**Example:**
```python
from seamstress.visualization import generate_two_hour_block_plan

plan = generate_two_hour_block_plan(
    projects=["Project A", "Project B", "Project C"],
    days=7
)
print(plan.head(10))
```

---

### render_block_plan()

```python
def render_block_plan(plan: pd.DataFrame) -> str
```

Formats plan DataFrame as human-readable text.

**Example:**
```python
from seamstress.visualization import generate_two_hour_block_plan, render_block_plan

plan = generate_two_hour_block_plan(["Project A", "Project B"], days=3)
text = render_block_plan(plan)
print(text)
# Output:
# Thu 08:00 → 10:00 | Project A
# Thu 10:00 → 12:00 | Project B
# ...
```

---

## Local LLM (`seamstress.local_models`)

### ollama_available()

```python
def ollama_available() -> bool
```

Checks if Ollama CLI is installed.

**Example:**
```python
from seamstress.local_models import ollama_available

if ollama_available():
    print("Ollama is ready")
else:
    print("Install Ollama from https://ollama.ai/")
```

---

### generate_summary_with_ollama()

```python
def generate_summary_with_ollama(
    notes: Iterable[str],
    model: str = "mistral"
) -> str
```

Generates text summary using local Ollama model.

**Raises:** `LocalModelUnavailable` if Ollama not found or model fails

**Example:**
```python
from seamstress.local_models import generate_summary_with_ollama

notes = [
    "Completed literature review of 5 papers",
    "Key finding: attention mechanisms improve t-SNE clustering",
    "Next: implement prototype in notebook"
]

summary = generate_summary_with_ollama(notes, model="mistral")
print(summary)
```

---

### save_summary()

```python
def save_summary(summary: str, path: Path) -> Path
```

Writes summary to file, creating directories as needed.

**Example:**
```python
from pathlib import Path
from seamstress.local_models import save_summary

summary = "This project achieved X, Y, and Z..."
output = save_summary(summary, Path("artifacts/summaries/project_nov.txt"))
print(f"Saved to {output}")
```

---

## Focus Monitor (`seamstress.focus`)

### FocusMonitor

Main class for live focus tracking.

```python
class FocusMonitor:
    def __init__(
        self,
        project: str,
        block_minutes: int = 120,
        break_after_minutes: int = 40,
        enable_webcam: bool = False
    )
    
    def run(self) -> WorkBlock
    def create_time_capsule(
        self,
        summary: str,
        resources: Iterable[str] = ()
    ) -> TimeCapsule
```

**Example:**
```python
from seamstress.focus import FocusMonitor

monitor = FocusMonitor(
    project="Bayesian Project",
    block_minutes=120,
    break_after_minutes=40,
    enable_webcam=False
)

# Runs until Ctrl+C or timeout
block = monitor.run()
print(f"Session complete: {block.duration} with score {block.focus_score}")

# Optionally create capsule afterward
capsule = monitor.create_time_capsule(
    summary="Completed Bayesian inference prototype",
    resources=["notebooks/bayes.ipynb"]
)
```

**Note:** Requires accessibility permissions on macOS.

---

## CLI Entry Point (`seamstress.cli`)

The CLI uses [Typer](https://typer.tiangolo.com/) for command routing. All commands documented in `USAGE_GUIDE.md` are implemented in this module.

### Custom Usage

You can import and call CLI functions programmatically:

```python
from seamstress.cli import app
from typer.testing import CliRunner

runner = CliRunner()
result = runner.invoke(app, ["board-view"])
print(result.stdout)
```

---

## Configuration

### Config File Location

`~/.seamstress/config.json`

**Structure:**
```json
{
  "ics_path": "/path/to/calendar.ics"
}
```

### State File Location

`~/.seamstress/state.json`

**Backup:** `state.json.bak` created on every write

### Thread Definitions

`data/threads.yaml` in project root

Reload after edits:
```bash
seamstress init
```

---

## Error Handling

### LocalModelUnavailable

Raised when Ollama CLI not found or fails.

```python
from seamstress.local_models import LocalModelUnavailable, generate_summary_with_ollama

try:
    summary = generate_summary_with_ollama(["note"])
except LocalModelUnavailable as e:
    print(f"LLM error: {e}")
```

---

## Type Hints

All modules use Python type hints for IDE support:

```python
from seamstress.data_models import WorkBlock, TimeCapsule
from datetime import datetime

def analyze_session(block: WorkBlock) -> dict[str, float]:
    return {
        "duration_hours": block.duration.total_seconds() / 3600,
        "score": block.focus_score
    }
```

Use `mypy` for static type checking:
```bash
mypy seamstress/
```

---

## Testing

### Manual Testing

```python
# Test state operations
from seamstress.storage import load_state
state = load_state()
assert len(state.projects) > 0

# Test ICS parsing
from seamstress.calendar_ics import import_ics
from pathlib import Path
events = import_ics(Path("data/samples/sample_calendar.ics"))
assert len(events) == 2
```

### Unit Tests (Future)

Planned structure:
```
tests/
  test_data_models.py
  test_storage.py
  test_calendar_ics.py
  test_focus_offline.py
  test_visualization.py
```

Run with pytest:
```bash
pytest tests/
```

---

## Examples

### Complete Workflow

```python
from seamstress.storage import load_state, save_state
from seamstress.data_models import WorkBlock, ProjectGoal
from seamstress.calendar_ics import import_ics
from seamstress.visualization import plot_weekly_blocks
from datetime import datetime, timedelta
from pathlib import Path

# 1. Load state
state = load_state()

# 2. Add a project goal
goal = ProjectGoal("New Project", weekly_target_hours=6)
state.register_project_goal(goal)

# 3. Simulate a work block
block = WorkBlock(
    start=datetime.now() - timedelta(hours=2),
    end=datetime.now(),
    project="New Project",
    focus_score=0.85
)
state.add_work_block(block)

# 4. Save state
save_state(state)

# 5. Import calendar
events = import_ics(Path("~/calendar.ics").expanduser())
print(f"Found {len(events)} upcoming events")

# 6. Visualize
plot_weekly_blocks(Path("artifacts/this_week.png"))
```

---

## Further Reading

- **Usage Guide:** `USAGE_GUIDE.md` - Command-line interface documentation
- **Roadmap:** `ROADMAP.md` - Future features and known issues
- **Test Results:** `TEST_RESULTS.md` - Current test coverage and status
- **Source Code:** `seamstress/` - Fully typed and documented

---

*API Reference v0.1.0*  
*Last updated: 2025-11-13*

