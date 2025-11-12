"""Visualization helpers for Seamstress."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List

import matplotlib.pyplot as plt
import pandas as pd
from rich.console import Console

from .data_models import WorkBlock
from .storage import iter_work_blocks, load_state

console = Console()


def work_blocks_to_dataframe(blocks: Iterable[WorkBlock]) -> pd.DataFrame:
    records = [
        {
            "project": block.project,
            "start": block.start,
            "end": block.end,
            "duration_hours": block.duration.total_seconds() / 3600,
            "focus_score": block.focus_score,
        }
        for block in blocks
    ]
    df = pd.DataFrame.from_records(records)
    if not df.empty:
        df["start"] = pd.to_datetime(df["start"])
        df["end"] = pd.to_datetime(df["end"])
    return df


def plot_weekly_blocks(output_path: Path) -> Path:
    state = load_state()
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    recent_blocks = [
        block for block in iter_work_blocks(state) if block.start >= week_ago
    ]
    if not recent_blocks:
        console.print("[yellow]No work blocks available for visualization.[/yellow]")
        return output_path
    df = work_blocks_to_dataframe(recent_blocks)
    df["day"] = df["start"].dt.date
    summary = df.groupby(["day", "project"]).agg({"duration_hours": "sum"}).reset_index()
    pivot = summary.pivot(index="day", columns="project", values="duration_hours").fillna(0)
    pivot.plot(kind="bar", stacked=True, figsize=(10, 6))
    plt.title("Focused Work — Last 7 Days")
    plt.xlabel("Day")
    plt.ylabel("Hours")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    console.print(f"[green]Saved visualization to {output_path}[/green]")
    return output_path


def generate_two_hour_block_plan(projects: List[str], days: int = 5) -> pd.DataFrame:
    now = datetime.utcnow().replace(hour=8, minute=0, second=0, microsecond=0)
    plan: List[dict] = []
    for day in range(days):
        start_of_day = now + timedelta(days=day)
        for block_index in range(4):  # four 2-hour blocks per day
            start = start_of_day + timedelta(hours=block_index * 2)
            end = start + timedelta(hours=2)
            project = projects[(day * 4 + block_index) % len(projects)]
            plan.append(
                {
                    "day": start.date(),
                    "start": start,
                    "end": end,
                    "project": project,
                }
            )
    return pd.DataFrame(plan)


def render_block_plan(plan: pd.DataFrame) -> str:
    rows = [
        f"{row['start']:%a %H:%M} → {row['end']:%H:%M} | {row['project']}"
        for _, row in plan.iterrows()
    ]
    return "\n".join(rows)
