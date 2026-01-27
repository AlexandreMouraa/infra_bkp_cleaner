import argparse
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, List


@dataclass
class Candidate:
    Path: Path
    size_bytes: int
    mtime: datetime



def bytes_to_human(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    f = float(n)
    for u in units:
        if f < 1024.0:
            return f"{f:.2f} {u}"
        f /= 1024.0
    return f"{f:.2f} PB"


def is_dangerous_path(p: Path) -> bool:

    rp = p.resolve()
    forbidden = {
        Path("/").resolve(),
        Path("/home").resolve(),
        Path("/root").resolve(),
    }
    try:
        forbidden.add(Path.home().resolve())
    except Exception:
        pass

    if rp in forbidden:
        return True
    
    #If it's too "short" as an example /mnt /var, it's not a prove, but it reduces risk
    #Adjust if it's blocking too much

    if len(rp.parts) <= 2:
        return True
    
    return False


def setup_logger(log_file: str | None) -> None:
    handlers: List[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
        handlers=handlers,
    )


def iter_files(base: Path, recursive: bool) -> Iterable[Path]:
    if recursive:
        yield from (p for p in base.rglob("*") if p.is_file())
    else:
        yield from(p for p in base.iterdir() if p.is_file())


