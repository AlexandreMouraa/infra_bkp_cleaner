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
    return f"{f:.2f} PB


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


def collect_candidates(base: Path, days: int, recursive: bool) -> List[Candidate]:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days = days)

    candidates: List[Candidate] = []
    for f in iter_files(base, recursive=recursive):
        try:
            st = f.stat()
        except FileNotFoundError:
            continue #If the file just miss, keep going
        mtime = datetime.fromtimestamp(st.st_mtime, tz= timezone.utc)
        if mtime < cutoff:
            candidates.append(Candidate(Path=f, size_bytes=st.st_size, mtime=mtime))

        candidates.sort(key=lambda c: c.mtime)
    return candidates
    

def delete_candidates(candidates: List[Candidate]) -> int:
    delete = 0
    for c in candidates:
        try:
            c.Path.unlink()
            delete += 1
            logging.info(f"DELETE: {c.Path} ({bytes_to_human(c.size_bytes)})")
        except FileNotFoundError:
            logging.warning(f"SKIP (NOT FOUND): {c.Path}")
        except PermissionError:
            logging.error(f"PERMISSION DENIED: {c.Path}")
        
    return delete


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="infra_bkp_cleaner",
        description="Remove arquivos mais antigos que N dias em um diretório de bkp's (with dry-run)."
    )

    p.add_argument("--path", required=True, help="Diretório dos backups (ex: /mnt/backup)")
    p.add_argument("--days", type=int, required=True, help="Quantos dias manter(retenção)")
    p.add_argument("--dry-run", action="store_true", help="Não apaga nada, só simula")
    p.add_argument("--force", action="store_true", help="Necessário apagar de verdade (sem prompt)")
    p.add_argument("--recursive", action="store_true", help="Varre subpastas")
    p.add_argument("--log", default=None, help="Arquivo de Log(ex: cleaner.log)")

    return p

def main() -> int:
    args = build_parser().parse_args()
    setup_logger(args.log)

    base = Path(args.Path)

    if not base.exists() or not base.is_dir():
        logging.error(f"Path inválido (não existe ou não é diretório): {base}")
        return 2
    
    