"""Thread and barge management utilities."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import yaml
from rich.console import Console
from rich.table import Table

from .data_models import Barge, ProjectGoal, SeamstressState, Thread
from .storage import load_state, save_state

console = Console()


DEFAULT_THREADS_FILE = Path("data/threads.yaml")


def load_threads_from_yaml(path: Path = DEFAULT_THREADS_FILE) -> List[Barge]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fp:
        payload = yaml.safe_load(fp) or {}
    barges: List[Barge] = []
    for barge_data in payload.get("barges", []):
        threads = [
            Thread(
                name=thread_data["name"],
                description=thread_data.get("description", ""),
                urgency_level=thread_data.get("urgency_level", 1),
                related_projects=thread_data.get("related_projects", []),
                tasks=thread_data.get("tasks", []),
            )
            for thread_data in barge_data.get("threads", [])
        ]
        expected = None
        if deadline := barge_data.get("expected_landfall"):
            expected = datetime.fromisoformat(deadline)
        barges.append(
            Barge(
                name=barge_data["name"],
                description=barge_data.get("description", ""),
                expected_landfall=expected,
                threads=threads,
            )
        )
    return barges


def initialize_board_from_yaml(path: Path = DEFAULT_THREADS_FILE) -> None:
    state = load_state()
    for barge in load_threads_from_yaml(path):
        state.upsert_barge(barge)
    save_state(state)


def display_seamstress_board(state: Optional[SeamstressState] = None) -> None:
    current = state or load_state()
    table = Table(title="Seamstress Board: Barges and Threads")
    table.add_column("Barge")
    table.add_column("Thread")
    table.add_column("Urgency")
    table.add_column("Tasks")
    table.add_column("Next Milestone")
    for barge in current.barges:
        milestone = "—"
        if barge.expected_landfall:
            delta = barge.expected_landfall - datetime.utcnow()
            milestone = f"{barge.expected_landfall.date()} ({_format_delta(delta)})"
        for thread in barge.threads:
            table.add_row(
                barge.name,
                thread.name,
                "🔥" * max(1, thread.urgency_level),
                "\n".join(thread.tasks) if thread.tasks else "—",
                milestone,
            )
    console.print(table)


def _format_delta(delta: timedelta) -> str:
    days = delta.days
    hours = delta.seconds // 3600
    return f"{days}d {hours}h"


def summarize_project_progress(state: Optional[SeamstressState] = None) -> Table:
    current = state or load_state()
    table = Table(title="Project Work Summary")
    table.add_column("Project")
    table.add_column("Goal (hrs/week)")
    table.add_column("Blocks/Week")
    table.add_column("Recorded Hours")
    table.add_column("Focus Score Avg")
    for project_name, goal in current.projects.items():
        blocks = [block for block in current.work_blocks if block.project == project_name]
        total_hours = sum(block.duration.total_seconds() for block in blocks) / 3600
        avg_focus = 0.0
        if blocks:
            avg_focus = sum(block.focus_score for block in blocks) / len(blocks)
        table.add_row(
            project_name,
            f"{goal.weekly_target_hours:.1f}",
            f"{goal.block_count_for_week():.1f}",
            f"{total_hours:.1f}",
            f"{avg_focus:.2f}",
        )
    return table


def register_default_goals() -> None:
    state = load_state()
    defaults = [
        ProjectGoal(project="Bayesian Project", weekly_target_hours=8),
        ProjectGoal(project="Computer Vision Project", weekly_target_hours=6),
        ProjectGoal(project="LLM Project", weekly_target_hours=6),
        ProjectGoal(project="Information Theory paper", weekly_target_hours=5),
        ProjectGoal(project="Data Mining Exam 2", weekly_target_hours=3),
    ]
    for goal in defaults:
        state.register_project_goal(goal)
    save_state(state)
