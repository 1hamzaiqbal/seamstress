from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List


@dataclass
class IcsEvent:
    summary: str
    start: datetime
    end: datetime
    location: str = ""
    uid: str = ""


def _parse_dt(value: str) -> datetime:
    """Parse timestamps like 20241107T140000Z or 20241107T140000."""
    fmt = "%Y%m%dT%H%M%SZ" if value.endswith("Z") else "%Y%m%dT%H%M%S"
    return datetime.strptime(value, fmt)


def _fallback_parse_ics(path: Path) -> List[IcsEvent]:
    lines = [ln.strip() for ln in Path(path).read_text().splitlines()]
    events: List[IcsEvent] = []
    record: dict[str, str] = {}
    in_event = False

    for line in lines:
        if line == "BEGIN:VEVENT":
            in_event, record = True, {}
            continue
        if line == "END:VEVENT" and in_event:
            in_event = False
            events.append(
                IcsEvent(
                    summary=record.get("SUMMARY", ""),
                    start=_parse_dt(record["DTSTART"]),
                    end=_parse_dt(record["DTEND"]),
                    location=record.get("LOCATION", ""),
                    uid=record.get("UID", ""),
                )
            )
            record = {}
            continue
        if in_event and ":" in line:
            key, value = line.split(":", 1)
            record[key] = value

    return events


def import_ics(path: Path) -> List[IcsEvent]:
    """Robust ICS import. Uses `ics` if present, else a tiny fallback parser."""
    try:
        from ics import Calendar  # type: ignore

        calendar = Calendar(Path(path).read_text())
        events: List[IcsEvent] = []
        for event in calendar.events:
            start = event.begin.datetime
            end = event.end.datetime
            events.append(
                IcsEvent(
                    summary=event.name or "(untitled)",
                    start=start,
                    end=end,
                    location=getattr(event, "location", "") or "",
                    uid=getattr(event, "uid", "") or "",
                )
            )
        return sorted(events, key=lambda entry: entry.start)
    except Exception:
        return sorted(_fallback_parse_ics(path), key=lambda entry: entry.start)

