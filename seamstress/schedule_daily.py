from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List, Tuple

BLOCK = timedelta(hours=2)
RITUAL = timedelta(minutes=30)


@dataclass
class Block:
    start: datetime
    end: datetime
    label: str
    source: str  # "thread", "routine", "calendar", "buffer"


def build_simple_schedule(
    day_start: datetime,
    projects: Iterable[str],
    events: Iterable[Tuple[datetime, datetime, str]],
    focus_blocks: int = 3,
) -> List[Block]:
    """Round-robin 2h blocks across projects, with 30m morning/evening rituals and calendar overlay."""
    current = day_start
    blocks: List[Block] = []

    # Morning ritual
    blocks.append(Block(start=current, end=current + RITUAL, label="Morning planning", source="routine"))
    current += RITUAL

    # Main focus blocks
    project_list = list(projects) or ["General"]
    for index in range(focus_blocks):
        project = project_list[index % len(project_list)]
        blocks.append(Block(start=current, end=current + BLOCK, label=f"{project} — 2h sprint", source="thread"))
        current += BLOCK

    last_end = current
    for start, end, title in sorted(events, key=lambda item: item[0]):
        if start.tzinfo is not None:
            start = start.astimezone().replace(tzinfo=None)
        if end.tzinfo is not None:
            end = end.astimezone().replace(tzinfo=None)
        if end <= day_start or start >= last_end:
            continue
        if blocks and blocks[-1].end < start and blocks[-1].source != "routine":
            blocks.append(Block(start=blocks[-1].end, end=start, label="Buffer / transit", source="buffer"))
        blocks.append(
            Block(
                start=max(start, day_start),
                end=min(end, last_end),
                label=title,
                source="calendar",
            )
        )

    # Evening ritual
    blocks.append(Block(start=current, end=current + RITUAL, label="Evening planning", source="routine"))
    return blocks

