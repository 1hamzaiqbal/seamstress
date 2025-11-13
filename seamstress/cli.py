"""Command line interface for the Seamstress MVP."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List

import typer
from rich.console import Console
from rich.panel import Panel

from . import board
from .calendar_ics import import_ics
from .calendar_sync import CalendarUnavailableError, fetch_upcoming_events, render_calendar_table
from .focus import run_focus_session
from .focus_offline import analyze, load_csv
from .local_models import LocalModelUnavailable, generate_summary_with_ollama, save_summary
from .schedule_daily import build_simple_schedule
from .storage import load_state
from .timecapsule import create_time_capsule
from .visualization import generate_two_hour_block_plan, plot_weekly_blocks, render_block_plan

app = typer.Typer(help="Seamstress productivity companion", add_completion=False)
console = Console()

CONFIG = Path.home() / ".seamstress" / "config.json"


def _get_cfg() -> dict:
    if CONFIG.exists():
        return json.loads(CONFIG.read_text())
    return {}


def _set_cfg(data: dict) -> None:
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(data, indent=2))


@app.command()
def focus(project: str, webcam: bool = typer.Option(False, help="Enable webcam focus detection")) -> None:
    """Start a focus session for a project."""
    console.print(f"Starting focus session for [bold]{project}[/bold]. Press Ctrl+C to stop early.")
    try:
        block = run_focus_session(project=project, use_webcam=webcam)
    except KeyboardInterrupt:
        console.print("\nSession interrupted before completion.")
        raise typer.Exit(code=1)
    console.print(
        Panel.fit(
            f"Recorded session from {block.start:%H:%M} to {block.end:%H:%M} with focus score {block.focus_score:.2f}",
            title="Session saved",
            border_style="green",
        )
    )


@app.command()
def board_view() -> None:
    """Display the Seamstress board."""
    state = load_state()
    board.display_seamstress_board(state)
    console.print(board.summarize_project_progress(state))


@app.command()
def init(defaults: bool = typer.Option(True, help="Seed default goals and threads")) -> None:
    """Initialize the local state store with default configuration."""
    if defaults:
        board.register_default_goals()
        threads_file = Path("data/threads.yaml")
        if threads_file.exists():
            board.initialize_board_from_yaml(threads_file)
    console.print("Initialized Seamstress state.")


@app.command()
def visualize(output: Path = typer.Option(Path("artifacts/weekly_focus.png"))) -> None:
    """Generate a stacked bar chart of the last week's focus blocks."""
    plot_weekly_blocks(output)


@app.command("visualize-daily")
def visualize_daily(
    start: str = typer.Option(..., help="ISO start, e.g. 2025-11-11T09:00"),
    focus_blocks: int = typer.Option(3, help="Number of 2-hour focus blocks"),
    ics_path: Path | None = typer.Option(None, help="Optional path to an ICS file for overlay"),
    out: Path = typer.Option(Path("artifacts/daily.png"), help="Output image path"),
) -> None:
    """Build a simple day plan with rituals and overlay ICS events."""
    try:
        import matplotlib.pyplot as plt
    except Exception:
        console.print("[red]matplotlib not installed. pip install -e .[viz][/red]")
        raise typer.Exit(code=1)

    start_dt = datetime.fromisoformat(start)
    state = load_state()
    projects = list(state.projects.keys()) or ["General"]

    cfg_path = _get_cfg().get("ics_path") or "~/.seamstress/calendar.ics"
    selected_path = (ics_path or Path(cfg_path)).expanduser()

    events_raw: List[tuple[datetime, datetime, str]] = []
    if selected_path.exists():
        for event in import_ics(selected_path):
            events_raw.append((event.start, event.end, event.summary))

    blocks = build_simple_schedule(start_dt, projects, events_raw, focus_blocks)
    if not blocks:
        console.print("[yellow]No schedule blocks generated.[/yellow]")
        return

    output_path = out.expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    base = blocks[0].start
    colors = {"thread": "#4C72B0", "routine": "#55A868", "calendar": "#C44E52", "buffer": "#8172B3"}

    fig, ax = plt.subplots(figsize=(11, 3))
    for block in blocks:
        left = (block.start - base).total_seconds() / 3600
        width = (block.end - block.start).total_seconds() / 3600
        ax.barh(
            [0],
            [width],
            left=left,
            height=0.35,
            color=colors.get(block.source, "#999"),
            edgecolor="black",
        )
        ax.text(
            left + width / 2,
            0,
            block.label,
            ha="center",
            va="center",
            fontsize=8,
            color="white" if block.source != "routine" else "black",
        )
    ax.set_xlabel("Hours from start")
    ax.set_yticks([])
    ax.set_title(start_dt.strftime("Seamstress — daily plan"))
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    console.print(Panel(f"Saved {output_path}", title="Daily visualization", border_style="green"))


@app.command()
def plan(days: int = typer.Option(5, help="Number of days to schedule")) -> None:
    """Generate a default rotation of 2-hour blocks across active projects."""
    state = load_state()
    projects = list(state.projects.keys())
    if not projects:
        console.print("[yellow]No projects configured. Run `seamstress init` first.[/yellow]")
        raise typer.Exit(code=1)
    plan_df = generate_two_hour_block_plan(projects=projects, days=days)
    console.print(Panel(render_block_plan(plan_df), title="Two-hour Sprint Plan"))


@app.command()
def calendar(horizon: int = typer.Option(7, help="Number of days to sync")) -> None:
    """Fetch and display upcoming Google Calendar events."""
    try:
        events = fetch_upcoming_events(horizon_days=horizon)
    except CalendarUnavailableError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error
    if events.empty:
        console.print("[yellow]No upcoming events found.[/yellow]")
        return
    console.print(Panel(render_calendar_table(events), title="Upcoming Events"))


@app.command("calendar-import-ics")
def calendar_import_ics(ics_path: Path) -> None:
    """Import and cache a path to an ICS file (no OAuth required)."""
    expanded = ics_path.expanduser()
    if not expanded.exists():
        console.print(f"[red]Not found:[/red] {expanded}")
        raise typer.Exit(code=1)
    cfg = _get_cfg()
    cfg["ics_path"] = str(expanded)
    _set_cfg(cfg)
    events = import_ics(expanded)
    console.print(Panel(f"Registered ICS: {expanded}\nEvents loaded: {len(events)}", title="Calendar"))


@app.command("focus-analyze")
def focus_analyze(csv_path: Path) -> None:
    """Offline analysis of focus CSV metrics."""
    expanded = csv_path.expanduser()
    if not expanded.exists():
        console.print(f"[red]Not found:[/red] {expanded}")
        raise typer.Exit(code=1)
    samples = load_csv(expanded)
    hints = analyze(samples)
    if not hints:
        console.print("No break suggestions.")
        return
    for hint in hints:
        console.print(f"{hint.start:%H:%M}–{hint.end:%H:%M} | {hint.reason}")


@app.command()
def capsule(
    project: str,
    summary: str = typer.Argument(..., help="Summary of the final 10 minutes"),
    resource: List[str] = typer.Option(
        [], "--resource", "-r", help="Paths or links to resources referenced in the capsule"
    ),
    include_probes: bool = typer.Option(
        True, "--probes/--no-probes", help="Capture context using macOS probes when available."
    ),
) -> None:
    """Manually create a time capsule entry for a project."""
    capsule = create_time_capsule(
        project=project,
        summary=summary,
        resources=resource,
        include_probes=include_probes,
    )
    console.print(Panel(f"Stored time capsule for {project}", title="Time Capsule", border_style="cyan"))


@app.command("streamlit")
def streamlit_dashboard() -> None:
    """Launch the local Streamlit dashboard (no cloud dependencies)."""
    import importlib.util

    if importlib.util.find_spec("streamlit") is None:
        console.print("[red]streamlit not installed. pip install -e .[gui][/red]")
        raise typer.Exit(code=1)
    module_path = Path(__file__).parent / "app_streamlit" / "dashboard.py"
    subprocess.run(["streamlit", "run", str(module_path)], check=False)


@app.command()
def summarize(project: str, output: Path = typer.Option(Path("artifacts/time_capsule_summary.txt"))) -> None:
    """Use a local LLM (Ollama) to summarize the latest time capsule for a project."""
    state = load_state()
    capsules = [capsule for capsule in state.time_capsules if capsule.project == project]
    if not capsules:
        console.print(f"[yellow]No time capsules found for project {project}.[/yellow]")
        raise typer.Exit(code=1)
    latest = max(capsules, key=lambda capsule: capsule.created_at)
    notes = [
        f"Project: {latest.project}",
        f"Captured at: {latest.created_at.isoformat()}",
        latest.summary,
    ] + latest.open_resources
    try:
        summary = generate_summary_with_ollama(notes)
    except LocalModelUnavailable as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error
    save_summary(summary, output)
    console.print(Panel(summary, title=f"LLM Summary → {output}"))


def run() -> None:
    app()


if __name__ == "__main__":
    run()
