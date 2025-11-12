"""Focus monitoring primitives for Seamstress."""
from __future__ import annotations

import importlib.util
import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Deque, Iterable, Optional

from rich.console import Console
from rich.live import Live
from rich.table import Table

from .data_models import TimeCapsule, WorkBlock
from .storage import load_state, save_state

console = Console()


@dataclass
class FocusEvent:
    timestamp: datetime
    intensity: float = 1.0


class FocusMonitor:
    """Monitors keyboard (and optional webcam) activity for a focus session."""

    def __init__(
        self,
        project: str,
        use_webcam: bool = False,
        block_minutes: int = 120,
        break_threshold_minutes: int = 40,
        idle_grace_minutes: int = 10,
    ) -> None:
        self.project = project
        self.use_webcam = use_webcam
        self.block_minutes = block_minutes
        self.break_threshold = timedelta(minutes=break_threshold_minutes)
        self.idle_grace = timedelta(minutes=idle_grace_minutes)
        self.events: Deque[FocusEvent] = deque(maxlen=4096)
        self.start_time = datetime.utcnow()
        self.last_break_prompt: Optional[datetime] = None
        self.webcam_available = self._webcam_supported() if use_webcam else False
        self._stop = threading.Event()
        self._keyboard_listener = None
        self._webcam_thread: Optional[threading.Thread] = None

    def _webcam_supported(self) -> bool:
        return importlib.util.find_spec("cv2") is not None

    def run(self) -> WorkBlock:
        self._start_keyboard_listener()
        self._start_webcam_monitor()
        with Live(self._render_table(), console=console, refresh_per_second=2) as live:
            while not self._stop.is_set():
                try:
                    time.sleep(5)
                except KeyboardInterrupt:
                    self.stop()
                    break
                live.update(self._render_table())
                if self._should_prompt_break():
                    console.print(
                        "[bold magenta]\nGentle reminder: you've been focused for a while. Consider a 5-minute break.[/bold magenta]"
                    )
                    self.last_break_prompt = datetime.utcnow()
                elapsed = datetime.utcnow() - self.start_time
                if elapsed >= timedelta(minutes=self.block_minutes):
                    self.stop()
        self._shutdown()
        return self._finalize_block()

    def _start_keyboard_listener(self) -> None:
        pynput_available = importlib.util.find_spec("pynput") is not None
        if not pynput_available:
            console.print(
                "[yellow]pynput not installed; keyboard activity will not be tracked.[/yellow]"
            )
            return
        from pynput import keyboard  # type: ignore

        def on_press(_key: object) -> None:
            self.events.append(FocusEvent(timestamp=datetime.utcnow(), intensity=1.0))

        self._keyboard_listener = keyboard.Listener(on_press=on_press)
        self._keyboard_listener.start()

    def _start_webcam_monitor(self) -> None:
        if not (self.use_webcam and self.webcam_available):
            if self.use_webcam:
                console.print("[yellow]OpenCV not available; webcam monitoring disabled.[/yellow]")
            return

        def loop() -> None:
            import cv2

            capture = cv2.VideoCapture(0)
            cascade = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"))
            try:
                while not self._stop.is_set():
                    ret, frame = capture.read()
                    if not ret:
                        time.sleep(1)
                        continue
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = cascade.detectMultiScale(gray, 1.3, 5)
                    intensity = 1.0 if len(faces) else 0.2
                    self.events.append(FocusEvent(timestamp=datetime.utcnow(), intensity=intensity))
                    time.sleep(10)
            finally:
                capture.release()

        self._webcam_thread = threading.Thread(target=loop, daemon=True)
        self._webcam_thread.start()

    def _aggregate_focus_score(self) -> float:
        if not self.events:
            return 0.0
        return sum(event.intensity for event in self.events) / len(self.events)

    def _should_prompt_break(self) -> bool:
        elapsed = datetime.utcnow() - self.start_time
        if elapsed < self.break_threshold:
            return False
        if self.last_break_prompt and datetime.utcnow() - self.last_break_prompt < self.idle_grace:
            return False
        idle_duration = self._estimate_idle_duration()
        return timedelta(minutes=5) <= idle_duration <= self.idle_grace

    def _estimate_idle_duration(self) -> timedelta:
        now = datetime.utcnow()
        while self.events and now - self.events[0].timestamp > self.idle_grace:
            self.events.popleft()
        if not self.events:
            return self.idle_grace
        return now - self.events[-1].timestamp

    def _render_table(self) -> Table:
        table = Table(title=f"Seamstress Focus Session — {self.project}")
        table.add_column("Metric")
        table.add_column("Value")
        elapsed = datetime.utcnow() - self.start_time
        table.add_row("Elapsed", str(timedelta(seconds=int(elapsed.total_seconds()))))
        table.add_row("Focus Score", f"{self._aggregate_focus_score():.2f}")
        table.add_row("Events captured", str(len(self.events)))
        table.add_row("Break threshold", str(self.break_threshold))
        table.add_row("Idle grace", str(self.idle_grace))
        table.add_row("Block length", f"{self.block_minutes} minutes")
        table.add_row("Webcam active", "Yes" if self.use_webcam and self.webcam_available else "No")
        return table

    def stop(self) -> None:
        self._stop.set()

    def _shutdown(self) -> None:
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        if self._webcam_thread and self._webcam_thread.is_alive():
            self._webcam_thread.join(timeout=1)
        self._webcam_thread = None

    def _finalize_block(self) -> WorkBlock:
        end_time = datetime.utcnow()
        block = WorkBlock(
            start=self.start_time,
            end=end_time,
            project=self.project,
            focus_score=self._aggregate_focus_score(),
        )
        state = load_state()
        state.add_work_block(block)
        save_state(state)
        return block

    def create_time_capsule(self, summary: str, resources: Optional[Iterable[str]] = None) -> TimeCapsule:
        state = load_state()
        capsule = TimeCapsule(
            project=self.project,
            created_at=datetime.utcnow(),
            summary=summary,
            open_resources=list(resources or []),
        )
        state.add_time_capsule(capsule)
        save_state(state)
        return capsule


def run_focus_session(project: str, use_webcam: bool = False) -> WorkBlock:
    monitor = FocusMonitor(project=project, use_webcam=use_webcam)
    try:
        return monitor.run()
    finally:
        monitor.stop()
