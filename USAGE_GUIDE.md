# Seamstress Usage Guide

## Overview

Seamstress is a productivity companion that combines quantified-self metrics with narrative planning. It tracks focus sessions, manages project goals through a "barges and threads" metaphor, and provides both CLI and GUI interfaces for planning and visualization.

**Version:** 0.1.0  
**Platform:** macOS (Apple Silicon recommended)  
**Python:** 3.10+

---

## Installation

### 1. Set Up Environment

```bash
# Clone or navigate to the repository
cd /path/to/seamstress

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install with all optional features
pip install -e '.[viz,calendar,vision,gui]'
```

### 2. Initialize State

```bash
# Seed default projects and threads from data/threads.yaml
seamstress init
```

This creates `~/.seamstress/state.json` with 5 default projects and barges loaded from `data/threads.yaml`.

---

## Core Commands

### Project & Thread Management

#### View the Board

```bash
seamstress board-view
```

Displays:
- All barges with their threads, urgency levels, and tasks
- Project progress summary with weekly targets vs. recorded hours
- Focus score averages per project
- Time until expected "landfall" (deadlines)

**Status:** ✅ Working  
**Output:** Rich-formatted tables in terminal

#### Generate Sprint Plan

```bash
seamstress plan --days 5
```

Creates a round-robin 2-hour sprint schedule across all active projects.

**Status:** ✅ Working  
**Output:** Formatted schedule showing day/time blocks by project

---

### Focus Tracking

#### Live Focus Session

```bash
seamstress focus "Bayesian Project"
```

Starts a 2-hour focus session with:
- Real-time keyboard activity tracking (via `pynput`)
- Focus score calculation
- Break prompts after 40 minutes of sustained work with low activity
- Automatic session end at 120 minutes

**With webcam (optional):**
```bash
seamstress focus "LLM Project" --webcam
```

Adds lightweight face detection for attention tracking.

**Status:** ✅ Working  
**Requirements:** 
- macOS Accessibility permissions for `pynput`
- Camera permissions for webcam mode
- OpenCV installed (`pip install opencv-python`)

**Note:** Sessions persist `WorkBlock` records to state on completion.

#### Offline Focus Analysis

```bash
seamstress focus-analyze data/samples/focus.csv
```

Analyzes pre-recorded CSV with columns: `timestamp`, `keystrokes`, `webcam_focus`

**Status:** ✅ Working  
**Sample data:** Included in `data/samples/focus.csv`  
**Output:** Break recommendations based on sustained low-focus windows

**Example output:**
```
09:40–09:40 | low focus 8m window (avg=0.32)
```

---

### Time Capsules

#### Create a Capsule

```bash
seamstress capsule "Bayesian Project" "Finished literature review" \
  --resource notebooks/analysis.ipynb \
  --resource https://arxiv.org/abs/1234.5678
```

Records a snapshot of work session end-state with:
- Summary text
- Resources (files, URLs, notes)
- Optional macOS context (Safari tabs, VSCode workspaces) via AppleScript probes

**Disable probes:**
```bash
seamstress capsule "Project" "Summary" --no-probes
```

**Status:** ✅ Working  
**Storage:** `~/.seamstress/state.json` under `time_capsules` array

#### Summarize with Local LLM

```bash
# Requires Ollama (brew install ollama)
ollama pull mistral

seamstress summarize "Bayesian Project"
```

Fetches the latest time capsule for the project and generates an AI summary.

**Status:** ⚠️ Functional but requires Ollama setup  
**Output:** `artifacts/time_capsule_summary.txt`

---

### Calendar Integration

#### ICS Import (No OAuth)

```bash
seamstress calendar-import-ics /path/to/calendar.ics
```

Registers an ICS file for use in daily visualization.

**Status:** ✅ Working  
**Config:** Stores path in `~/.seamstress/config.json`  
**Sample:** `data/samples/sample_calendar.ics` included

#### Google Calendar Sync (OAuth)

```bash
seamstress calendar --horizon 14
```

Fetches events from Google Calendar (next 14 days).

**Status:** ✅ Code present, requires OAuth setup  
**Requirements:**
- `credentials.json` from Google Cloud Console in `~/.seamstress/`
- First run triggers OAuth consent flow
- Token cached in `~/.seamstress/token.json`

---

### Visualizations

#### Daily Timeline

```bash
seamstress visualize-daily --start 2025-11-11T09:00 --out artifacts/daily.png
```

Creates a horizontal timeline showing:
- Morning/evening rituals (30min blocks)
- 2-hour sprints per project
- Calendar events overlaid (from registered ICS)
- Buffer/transit time between events

**Status:** ✅ Working  
**Output:** PNG file with matplotlib-rendered timeline

#### Weekly Focus Chart

```bash
seamstress visualize --output artifacts/weekly_focus.png
```

Generates stacked bar chart of focus hours by project over the last 7 days.

**Status:** ✅ Working (requires existing WorkBlock data)  
**Note:** Currently shows "No work blocks available" if no sessions have been completed

---

### Streamlit Dashboard

```bash
seamstress streamlit
```

Launches an interactive web dashboard showing:
- Project targets and progress
- Time capsule history
- ICS calendar import/viewer

**Status:** ✅ Code present, not tested in this session  
**Port:** Default Streamlit port (usually 8501)  
**Requirements:** `pip install -e '.[gui]'`

---

## Data Model

### State Storage

Location: `~/.seamstress/state.json`

**Structure:**
```json
{
  "projects": {
    "Project Name": {
      "weekly_target_hours": 8,
      "block_minutes": 120
    }
  },
  "work_blocks": [
    {
      "start": "2025-11-13T10:00:00.000000Z",
      "end": "2025-11-13T12:00:00.000000Z",
      "project": "Bayesian Project",
      "focus_score": 0.82
    }
  ],
  "time_capsules": [...],
  "barges": [...]
}
```

### Configuration

Location: `~/.seamstress/config.json`

Stores:
- `ics_path`: Currently registered ICS calendar file

### Thread Definitions

Location: `data/threads.yaml`

Defines barges (projects) with nested threads (sub-goals), urgency levels, and task lists.

**Reload after edits:**
```bash
seamstress init
```

---

## Feature Status Matrix

| Feature | Status | Notes |
|---------|--------|-------|
| Project/Thread management | ✅ Working | Board view, YAML import |
| Focus sessions (keyboard) | ✅ Working | Requires accessibility permissions |
| Focus sessions (webcam) | ✅ Working | Requires camera permissions |
| Offline focus analysis | ✅ Working | CSV format documented |
| Time capsules | ✅ Working | With/without macOS probes |
| LLM summarization | ⚠️ Requires setup | Needs Ollama installed |
| Sprint planning | ✅ Working | Round-robin 2h blocks |
| ICS calendar import | ✅ Working | Fallback parser if `ics` lib missing |
| Google Calendar sync | ⚠️ Requires OAuth | Credentials setup needed |
| Daily timeline viz | ✅ Working | PNG export with events overlay |
| Weekly focus viz | ✅ Working | Requires recorded work blocks |
| Streamlit dashboard | ⚠️ Not tested | Code present, should work |
| State serialization | ✅ Working | Fixed in unify/v3-plus branch |

---

## Known Issues

### 1. Weekly Visualization Empty
**Symptom:** `visualize` command shows "No work blocks available"  
**Cause:** No completed focus sessions yet  
**Fix:** Run at least one `seamstress focus` session to completion

### 2. Timezone Handling in Daily Viz
**Status:** Fixed in current version  
**Solution:** ICS events now normalized to naive datetime before comparison

### 3. YAML Task Parsing
**Status:** Fixed in current version  
**Solution:** Non-string task items (dicts) are now flattened to strings

### 4. Old State Files
**Issue:** State files from earlier versions may not load  
**Solution:** Backup exists at `~/.seamstress/state.json.bak`  
**Recovery:** Delete `state.json` and run `seamstress init`

---

## Troubleshooting

### Accessibility Permissions

If `pynput` fails:
1. Open System Settings → Privacy & Security → Accessibility
2. Add Terminal (or your terminal app)
3. Restart terminal and retry

### Camera Permissions

If webcam mode fails:
1. Open System Settings → Privacy & Security → Camera
2. Add Terminal
3. Restart and retry with `--webcam`

### Missing Dependencies

```bash
# For visualization
pip install matplotlib

# For webcam focus
pip install opencv-python pynput

# For ICS import (optional, has fallback)
pip install ics

# For GUI dashboard
pip install streamlit pandas

# For Google Calendar
pip install google-api-python-client google-auth-oauthlib
```

### State Corruption

```bash
# Backup current state
cp ~/.seamstress/state.json ~/.seamstress/state.json.backup

# Reset to fresh state
rm ~/.seamstress/state.json
seamstress init
```

---

## Development & Testing

### Run Smoke Tests

```bash
# Check syntax
python -m compileall seamstress

# Test CLI loads
seamstress --help

# Test imports
python -c "from seamstress.storage import load_state; print('OK')"
```

### Sample Data

- `data/threads.yaml` - Default project/thread definitions
- `data/samples/focus.csv` - Focus tracking test data
- `data/samples/sample_calendar.ics` - Calendar events for visualization

### Artifacts Directory

Generated outputs saved to `artifacts/`:
- `daily_smoke.png` - Daily timeline visualizations
- `weekly_focus.png` - Weekly stacked bar charts
- `time_capsule_summary.txt` - LLM summaries

---

## Quick Start Workflow

```bash
# 1. Initialize
seamstress init

# 2. View current board
seamstress board-view

# 3. Generate a weekly plan
seamstress plan --days 7

# 4. Import a calendar
seamstress calendar-import-ics data/samples/sample_calendar.ics

# 5. Visualize a day
seamstress visualize-daily --start 2025-11-15T09:00

# 6. Run a focus session (keyboard only)
seamstress focus "Bayesian Project"

# 7. Create a time capsule afterward
seamstress capsule "Bayesian Project" "Completed initial analysis" \
  --resource notes.md

# 8. Analyze offline focus data
seamstress focus-analyze data/samples/focus.csv
```

---

## Next Steps

See `ROADMAP.md` for planned features and known limitations.

