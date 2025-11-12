"""Persistence helpers for Seamstress state."""
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Type, TypeVar

from .data_models import (
    Barge,
    ProjectGoal,
    SeamstressState,
    Thread,
    TimeCapsule,
    WorkBlock,
)

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
STATE_FILE = Path.home() / ".seamstress" / "state.json"

T = TypeVar("T")


def _encode_dataclass(value: Any) -> Any:
    if is_dataclass(value):
        return {"__type__": value.__class__.__name__, **{
            key: _encode_dataclass(item) for key, item in asdict(value).items()
        }}
    if isinstance(value, datetime):
        return {"__datetime__": value.strftime(ISO_FORMAT)}
    if isinstance(value, Path):
        return {"__path__": str(value)}
    if isinstance(value, list):
        return [_encode_dataclass(item) for item in value]
    if isinstance(value, dict):
        return {key: _encode_dataclass(item) for key, item in value.items()}
    return value


def _decode_datetime(value: Dict[str, str]) -> datetime:
    return datetime.strptime(value["__datetime__"], ISO_FORMAT)


def _decode_dataclass(value: Dict[str, Any]) -> Any:
    type_name = value.pop("__type__", None)
    if not type_name:
        return {
            key: _decode(item) for key, item in value.items()
        }
    mapping: Dict[str, Type[Any]] = {
        "WorkBlock": WorkBlock,
        "ProjectGoal": ProjectGoal,
        "TimeCapsule": TimeCapsule,
        "Thread": Thread,
        "Barge": Barge,
    }
    cls = mapping[type_name]
    return cls(**{key: _decode(item) for key, item in value.items()})


def _decode(value: Any) -> Any:
    if isinstance(value, dict) and "__datetime__" in value:
        return _decode_datetime(value)
    if isinstance(value, dict) and "__path__" in value:
        return Path(value["__path__"])
    if isinstance(value, dict) and "__type__" in value:
        return _decode_dataclass(value)
    if isinstance(value, list):
        return [_decode(item) for item in value]
    return value


def load_state(state_path: Path | None = None) -> SeamstressState:
    path = state_path or STATE_FILE
    if not path.exists():
        return SeamstressState()
    with path.open("r", encoding="utf-8") as fp:
        payload = json.load(fp)
    data = _decode(payload)
    projects = {name: project for name, project in data.get("projects", {}).items()}
    work_blocks = data.get("work_blocks", [])
    time_capsules = data.get("time_capsules", [])
    barges = data.get("barges", [])
    return SeamstressState(
        projects=projects,
        work_blocks=work_blocks,
        time_capsules=time_capsules,
        barges=barges,
    )


def save_state(state: SeamstressState, state_path: Path | None = None) -> None:
    path = state_path or STATE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(_encode_dataclass(state), fp, indent=2)


def iter_work_blocks(state: SeamstressState, project: str | None = None) -> Iterable[WorkBlock]:
    for block in state.work_blocks:
        if project and block.project != project:
            continue
        yield block
