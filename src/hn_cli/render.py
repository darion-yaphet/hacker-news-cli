from __future__ import annotations

import json
import sys
from typing import Any, TextIO

from rich.console import Console


def _console() -> Console:
    return Console(record=True, force_terminal=False, color_system=None, no_color=True)


def print_json(payload: Any, stream: TextIO = sys.stdout) -> None:
    console = _console()
    console.print_json(data=payload)
    stream.write(console.export_text())


def print_error(message: str, code: int = 1, details: dict | None = None) -> None:
    error = {"message": message, "code": code}
    if details:
        error["details"] = details
    print_json({"error": error}, stream=sys.stderr)
