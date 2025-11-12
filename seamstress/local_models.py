"""Integration helpers for locally hosted language models."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Iterable

OLLAMA_COMMAND = shutil.which("ollama")
DEFAULT_MODEL = "mistral"


class LocalModelUnavailable(RuntimeError):
    pass


def ollama_available() -> bool:
    return OLLAMA_COMMAND is not None


def generate_summary_with_ollama(notes: Iterable[str], model: str = DEFAULT_MODEL) -> str:
    if not ollama_available():
        raise LocalModelUnavailable(
            "Ollama CLI not found. Install from https://ollama.ai/download and ensure it is on your PATH."
        )
    prompt = "\n".join(notes)
    command = [OLLAMA_COMMAND or "ollama", "run", model]
    process = subprocess.run(
        command,
        input=prompt.encode("utf-8"),
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        raise LocalModelUnavailable(process.stderr.decode("utf-8"))
    return process.stdout.decode("utf-8").strip()


def save_summary(summary: str, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(summary, encoding="utf-8")
    return path
