from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional

from .data_models import TimeCapsule
from .storage import load_state, save_state


@dataclass
class Probe:
    description: str
    command: List[str]


def suggest_macos_probes() -> List[Probe]:
    return [
        Probe(
            "Safari tabs",
            ["osascript", "-e", 'tell application "Safari" to get URL of every tab of every window'],
        ),
        Probe(
            "VSCode workspaces",
            ["osascript", "-e", 'tell application "Visual Studio Code" to get path of every workspace folder'],
        ),
    ]


def run_probe(command: List[str]) -> Optional[str]:
    try:
        result = subprocess.run(command, capture_output=True, check=False)
        if result.returncode == 0:
            return result.stdout.decode("utf-8").strip()
    except Exception:
        return None
    return None


def create_time_capsule(
    project: str,
    summary: str,
    resources: Iterable[str] = (),
    include_probes: bool = True,
) -> TimeCapsule:
    extras: List[str] = []
    if include_probes and platform.system() == "Darwin":
        for probe in suggest_macos_probes():
            result = run_probe(probe.command)
            if result:
                extras.append(f"{probe.description}: {result}")

    capsule = TimeCapsule(
        project=project,
        created_at=datetime.utcnow(),
        summary=summary,
        open_resources=list(resources) + extras,
    )

    state = load_state()
    state.add_time_capsule(capsule)
    save_state(state)
    return capsule

