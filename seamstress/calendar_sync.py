"""Google Calendar integration helpers."""
from __future__ import annotations

import importlib.util
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import pandas as pd

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
DEFAULT_TOKEN_PATH = Path.home() / ".seamstress" / "token.json"
DEFAULT_CREDENTIALS_PATH = Path.home() / ".seamstress" / "credentials.json"


class CalendarUnavailableError(RuntimeError):
    pass


def _google_client_available() -> bool:
    return all(
        importlib.util.find_spec(module) is not None
        for module in [
            "googleapiclient.discovery",
            "google_auth_oauthlib.flow",
            "google.auth.transport.requests",
        ]
    )


def _build_calendar_service(token_path: Path, credentials_path: Path):
    if not _google_client_available():
        raise CalendarUnavailableError(
            "Google API client libraries are not installed. Install google-api-python-client and google-auth-oauthlib."
        )
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with token_path.open("w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    return service


def fetch_upcoming_events(
    calendar_id: str = "primary",
    horizon_days: int = 7,
    token_path: Path = DEFAULT_TOKEN_PATH,
    credentials_path: Path = DEFAULT_CREDENTIALS_PATH,
) -> pd.DataFrame:
    """Fetch upcoming calendar events into a dataframe."""
    service = _build_calendar_service(token_path, credentials_path)
    now = datetime.utcnow().isoformat() + "Z"
    horizon = (datetime.utcnow() + timedelta(days=horizon_days)).isoformat() + "Z"
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=now,
            timeMax=horizon,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    records: List[dict] = []
    for event in events:
        start_str = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date")
        end_str = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date")
        start = pd.to_datetime(start_str)
        end = pd.to_datetime(end_str)
        records.append(
            {
                "summary": event.get("summary", "(no title)"),
                "start": start,
                "end": end,
                "duration_hours": (end - start).total_seconds() / 3600,
                "hangout_link": event.get("hangoutLink"),
            }
        )
    return pd.DataFrame.from_records(records)


def events_to_work_blocks(events: pd.DataFrame, project_mapping: Optional[dict[str, str]] = None) -> List[dict]:
    mapping = project_mapping or {}
    blocks: List[dict] = []
    for _, row in events.iterrows():
        project = mapping.get(row["summary"], "General")
        blocks.append(
            {
                "project": project,
                "start": row["start"],
                "end": row["end"],
                "duration_hours": row["duration_hours"],
            }
        )
    return blocks


def render_calendar_table(events: pd.DataFrame) -> str:
    if events.empty:
        return "No upcoming events found."
    rows = [
        f"{row['start']:%a %m-%d %H:%M} → {row['end']:%H:%M} | {row['summary']}"
        for _, row in events.iterrows()
    ]
    return "\n".join(rows)
