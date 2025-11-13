from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from ..calendar_ics import import_ics
from ..storage import load_state

st.set_page_config(page_title="Seamstress", layout="wide")


def _project_df(state):
    rows = []
    for name, goal in state.projects.items():
        rows.append({"Project": name, "Weekly target (h)": goal.weekly_target_hours})
    return pd.DataFrame(rows)


def _capsules_df(state):
    rows = []
    for capsule in state.time_capsules:
        rows.append({"Project": capsule.project, "When": capsule.created_at, "Summary": capsule.summary})
    return pd.DataFrame(rows).sort_values("When", ascending=False)


def _ics_df(path: Path | None):
    if not path or not path.exists():
        return pd.DataFrame()
    events = import_ics(path)
    return pd.DataFrame(
        [{"Title": event.summary, "Start": event.start, "End": event.end, "Location": event.location} for event in events]
    )


def main():
    st.title("Seamstress Control Board")
    state = load_state()
    left, right = st.columns([2, 1])
    with left:
        st.subheader("Projects")
        st.dataframe(_project_df(state), hide_index=True)
        st.subheader("Time Capsules")
        st.dataframe(_capsules_df(state), hide_index=True)
    with right:
        st.subheader("Calendar (ICS)")
        default_ics = Path("~/.seamstress/calendar.ics").expanduser()
        ics_path = st.text_input("ICS path", value=str(default_ics))
        if st.button("Load ICS"):
            dataframe = _ics_df(Path(ics_path).expanduser())
            if dataframe.empty:
                st.info("No events loaded.")
            else:
                st.dataframe(dataframe, hide_index=True, height=320)


if __name__ == "__main__":
    main()

