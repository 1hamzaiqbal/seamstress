"""Core data models for the Seamstress productivity system."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class WorkBlock:
    """Represents a contiguous block of focused work."""

    start: datetime
    end: datetime
    project: str
    focus_score: float

    @property
    def duration(self) -> timedelta:
        return self.end - self.start


@dataclass
class ProjectGoal:
    """Configuration for per-project time investment goals."""

    project: str
    weekly_target_hours: float
    block_minutes: int = 120

    def block_count_for_week(self) -> float:
        return (self.weekly_target_hours * 60) / self.block_minutes


@dataclass
class TimeCapsule:
    """Snapshot of the final minutes of a work session."""

    project: str
    created_at: datetime
    summary: str
    open_resources: List[str] = field(default_factory=list)
    memo_path: Optional[Path] = None


@dataclass
class Thread:
    name: str
    description: str
    urgency_level: int
    related_projects: List[str] = field(default_factory=list)
    tasks: List[str] = field(default_factory=list)


@dataclass
class Barge:
    name: str
    description: str
    expected_landfall: Optional[datetime] = None
    threads: List[Thread] = field(default_factory=list)


@dataclass
class SeamstressState:
    """Root document tracked in the local datastore."""

    projects: Dict[str, ProjectGoal] = field(default_factory=dict)
    work_blocks: List[WorkBlock] = field(default_factory=list)
    time_capsules: List[TimeCapsule] = field(default_factory=list)
    barges: List[Barge] = field(default_factory=list)

    def add_work_block(self, block: WorkBlock) -> None:
        self.work_blocks.append(block)

    def add_time_capsule(self, capsule: TimeCapsule) -> None:
        self.time_capsules.append(capsule)

    def register_project_goal(self, goal: ProjectGoal) -> None:
        self.projects[goal.project] = goal

    def upsert_barge(self, barge: Barge) -> None:
        for index, existing in enumerate(self.barges):
            if existing.name == barge.name:
                self.barges[index] = barge
                return
        self.barges.append(barge)

    def iter_threads(self) -> Iterable[Thread]:
        for barge in self.barges:
            yield from barge.threads
