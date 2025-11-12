"""Command line interface for the Seamstress MVP."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

import typer
from rich.console import Console
from rich.panel import Panel

from . import board
from .calendar_sync import CalendarUnavailableError, fetch_upcoming_events, render_calendar_table
from .focus import run_focus_session
from .local_models import LocalModelUnavailable, generate_summary_with_ollama, save_summary
from .storage import load_state, save_state
from .data_models import TimeCapsule
from .visualization import generate_two_hour_block_plan, plot_weekly_blocks, render_block_plan

app = typer.Typer(help="Seamstress productivity companion")
console = Console()


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


@app.command()
def capsule(
    project: str,
    summary: str = typer.Argument(..., help="Summary of the final 10 minutes"),
    resource: List[str] = typer.Option(
        [], "--resource", "-r", help="Paths or links to resources referenced in the capsule"
    ),
) -> None:
    """Manually create a time capsule entry for a project."""
    state = load_state()
    capsule = TimeCapsule(
        project=project,
        created_at=datetime.utcnow(),
        summary=summary,
        open_resources=resource,
    )
    state.add_time_capsule(capsule)
    save_state(state)
    console.print(Panel(f"Stored time capsule for {project}", title="Time Capsule", border_style="cyan"))


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
