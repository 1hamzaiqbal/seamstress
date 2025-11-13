# Seamstress MVP

This repository contains an initial implementation of **Seamstress**, a focus and project-tracking companion that blends quantified self metrics with narrative planning. The MVP aims to capture the requirements outlined in the original brief:

* Focus state monitoring using keystrokes and optional webcam activity.
* Break suggestions triggered after 40+ minutes of continuous work and low activity.
* Session "time capsules" that archive the final 10 minutes of a sprint.
* Project-aware time tracking with two-hour sprint planning.
* Visualization and summaries that show progress toward barge-level goals.
* Thread/Calendar alignment with two-hour blocks, plus Google Calendar import.
* Local language model helpers to summarize time capsules without cloud services.

The stack is designed to run on macOS (Apple Silicon) with local-first tooling. All components are written in Python and can be driven from the command line.

## Getting started

1. **Install Python 3.10+** (macOS ships 3.11 via Homebrew: `brew install python`).
2. **Create a virtual environment**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -e .
   ```

4. **Seed the default projects and threads**:

   ```bash
   seamstress init
   ```

   This loads the barges/threads defined in [`data/threads.yaml`](data/threads.yaml) and registers baseline project goals.

## Focus monitoring

Run a focus session tied to a project:

```bash
seamstress focus "Bayesian Project"
```

Keyboard activity is tracked via [`pynput`](https://pynput.readthedocs.io/). On macOS the first run will prompt for Accessibility permissions (System Settings → Privacy & Security → Accessibility). To include lightweight webcam attention signals, pass `--webcam` (requires `opencv-python`):

```bash
seamstress focus "LLM Project" --webcam
```

The focus monitor renders live metrics and emits a gentle reminder after 40 minutes of continuous work if the last 5–10 minutes show low activity. Sessions automatically end after the configured block length (120 minutes by default); pressing `Ctrl+C` also ends the session gracefully and persists a `WorkBlock` to `~/.seamstress/state.json`.

### Time capsules

Within a session you can capture the final minutes by calling into the `FocusMonitor.create_time_capsule` helper from another script or REPL:

```python
from seamstress.focus import FocusMonitor

monitor = FocusMonitor(project="Bayesian Project")
# ... run session ...
monitor.create_time_capsule(
    "Captured notes from MF-CLIP analysis",
    resources=["notebooks/mf_clip.ipynb", "https://arxiv.org/abs/1803.08494"],
)
```

Time capsules persist the summary, resource list, and optional memo path for later recall.

Alternatively, record a capsule straight from the CLI after a sprint:

```bash
seamstress capsule "LLM Project" "Captured final debugging steps" \
  --resource notebooks/llm_experiments.ipynb \
  --resource "Message Kevin re: hackathon"
```

## Threads, barges, and planning

The `board` command prints the current Seamstress board along with aggregated progress toward weekly hour goals:

```bash
seamstress board-view
```

Threads map directly to the "ships toward shore" metaphor—each barge in [`data/threads.yaml`](data/threads.yaml) contains threads with urgency levels and actionable tasks (including the immediate actions listed in the brief). You can edit this file and re-run `seamstress init` to sync updates into the state store.

Generate a default rotation of two-hour sprints across active projects:

```bash
seamstress plan --days 7
```

This produces a formatted schedule that can be transferred into your Seamstress board or calendar.

## Visualizations

The MVP ships with a simple Matplotlib visualization that stacks focused hours per project over the last seven days:

```bash
seamstress visualize --output artifacts/weekly_focus.png
```

The resulting chart can be embedded into weekly reviews or progress documents.

## Calendar integration

To align threads with real-world commitments, Seamstress can pull events from Google Calendar. Place your OAuth client credentials in `~/.seamstress/credentials.json` (downloaded from the Google Cloud Console) and run:

```bash
seamstress calendar --horizon 14
```

The first run launches the standard OAuth consent flow. Events are displayed in the terminal and can be mapped into the two-hour work-block rotation. Helper utilities in [`seamstress/calendar_sync.py`](seamstress/calendar_sync.py) can also convert events into work-block records for further analysis.

## Local LLM summaries

For a fully local workflow you can summarize time capsules using [Ollama](https://ollama.ai/) models on Apple Silicon:

```bash
brew install ollama
ollama pull mistral
seamstress summarize "LLM Project"
```

The command fetches the latest time capsule for the project, sends its notes to the selected Ollama model, and saves the generated summary to `artifacts/time_capsule_summary.txt`.

## Data model overview

State is persisted as JSON with the following entities:

* `WorkBlock` — start/end timestamps, project label, aggregated focus score.
* `ProjectGoal` — weekly hour targets and default two-hour block size.
* `TimeCapsule` — summary of the final 10 minutes of a session, plus resources and optional memo path.
* `Thread` / `Barge` — hierarchical planning constructs that mirror the "threads" and "ships" narrative.

Explore [`seamstress/data_models.py`](seamstress/data_models.py) for the full schema and helper methods.

## Documentation

Comprehensive documentation is available:

- **[Usage Guide](USAGE_GUIDE.md)** - Complete CLI command reference and workflows
- **[API Reference](API_REFERENCE.md)** - Python API for programmatic use
- **[Roadmap](ROADMAP.md)** - Planned features and architecture decisions
- **[Test Results](TEST_RESULTS.md)** - Current test coverage and feature status
- **[Status Summary](STATUS_SUMMARY.md)** - Project health, known issues, and next steps

## Quick Start

```bash
# Install with all features
pip install -e '.[viz,calendar,vision,gui]'

# Interactive setup wizard (recommended for first-time users)
seamstress setup

# OR initialize manually
seamstress init

# Verify system health
seamstress health-check

# View your board
seamstress board-view

# Generate a 7-day plan
seamstress plan --days 7

# Add work blocks manually (great for testing!)
seamstress add-work-block "Bayesian Project" --start "10:00" --end "12:00"

# Visualize your week
seamstress visualize --output artifacts/weekly_focus.png

# Run a focus session (requires accessibility permissions)
seamstress focus "Bayesian Project"

# Create a time capsule
seamstress capsule "Project" "What you accomplished" --resource notes.md
```

## Development

Run linting and unit tests (add your preferred tools; Pytest is recommended). A minimal smoke-test workflow could look like:

```bash
python -m compileall seamstress
```

### Current Status (v0.1.0 - Updated Nov 13, 2025)

✅ **Working Features:**
- Focus tracking (keyboard + webcam)
- Project/thread management via barges
- Time capsules with macOS context probes
- ICS calendar import and visualization
- Daily/weekly timeline generation
- Offline focus analysis
- Local LLM summarization (Ollama)
- Streamlit dashboard
- **NEW:** Manual work block entry (`add-work-block`)
- **NEW:** System health check (`health-check`)
- **NEW:** Interactive setup wizard (`setup`)
- **NEW:** Debug logging for troubleshooting

✅ **Recently Fixed:**
- Sample deadlines updated to 2025-2026
- Weekly visualization tested with data
- Work block persistence verified
- All high-priority bugs resolved

⚠️ **Requires Setup:**
- Google Calendar sync (needs OAuth)
- Live focus sessions (needs macOS permissions)

**Total Commands:** 16 (13 fully tested, 3 interactive)

See [Status Summary](STATUS_SUMMARY.md) for detailed test results and [Roadmap](ROADMAP.md) for planned enhancements.

## Contributing

Contributions are welcome—extend the MVP with additional automations, analytics, or integrations that keep the barges headed for shore.

Priority areas:
- Automated test suite (pytest)
- Windows/Linux platform support
- Enhanced visualizations
- User experience improvements

See [Roadmap](ROADMAP.md) for detailed contribution opportunities.
