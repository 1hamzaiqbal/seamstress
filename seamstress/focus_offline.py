from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List


@dataclass
class Sample:
    t: datetime
    keys: int
    webcam: float

    @property
    def score(self) -> float:
        return 0.7 * min(self.keys / 60, 1.0) + 0.3 * max(0.0, min(self.webcam, 1.0))


@dataclass
class BreakHint:
    start: datetime
    end: datetime
    reason: str


def load_csv(path: Path) -> List[Sample]:
    rows: List[Sample] = []
    with Path(path).open() as file_handle:
        reader = csv.DictReader(file_handle)
        for row in reader:
            rows.append(
                Sample(
                    t=datetime.fromisoformat(row["timestamp"]),
                    keys=int(row["keystrokes"]),
                    webcam=float(row.get("webcam_focus", 0.0)),
                )
            )
    return rows


def analyze(
    samples: List[Sample],
    sustained_min: int = 40,
    low_win_min: int = 8,
    thresh: float = 0.45,
) -> List[BreakHint]:
    hints: List[BreakHint] = []
    if not samples:
        return hints

    session_start = samples[0].t
    window: List[Sample] = []

    for sample in samples:
        window.append(sample)
        # keep last low_win_min worth of samples (assume ~5min cadence typical)
        while len(window) >= 2 and (sample.t - window[0].t) >= timedelta(minutes=low_win_min):
            window.pop(0)

        if (sample.t - session_start) >= timedelta(minutes=sustained_min):
            average = sum(item.score for item in window) / len(window) if window else 1.0
            if average < thresh:
                hints.append(
                    BreakHint(
                        start=window[0].t,
                        end=sample.t,
                        reason=f"low focus {low_win_min}m window (avg={average:.2f})",
                    )
                )
                session_start = sample.t
                window = [sample]

    return hints

