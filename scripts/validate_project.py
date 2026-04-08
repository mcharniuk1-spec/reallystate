from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def check_json(path: Path) -> None:
    json.loads(path.read_text(encoding="utf-8"))
    print(f"json ok: {path}")


def check_zip(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)
    with zipfile.ZipFile(path) as zf:
        bad = zf.testzip()
    if bad:
        raise RuntimeError(f"corrupt zip member in {path}: {bad}")
    print(f"office package ok: {path}")


def check_pdf(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)
    header = path.read_bytes()[:8]
    if not header.startswith(b"%PDF-"):
        raise RuntimeError(f"invalid pdf header: {path}")
    print(f"pdf ok: {path}")


def main() -> int:
    checks = [
        lambda: check_json(ROOT / "data/source_registry.json"),
        lambda: check_json(ROOT / ".cursor/mcp.json"),
        lambda: check_json(ROOT / ".cursor/environment.json"),
        lambda: check_json(ROOT / "package.json"),
        lambda: check_zip(ROOT / "docs/exports/bulgaria-real-estate-source-links.xlsx"),
        lambda: check_zip(ROOT / "docs/exports/bulgaria-real-estate-source-report.docx"),
        lambda: check_zip(ROOT / "docs/exports/project-status-roadmap.docx"),
        lambda: check_pdf(ROOT / "docs/exports/project-architecture-execution-guide.pdf"),
        lambda: subprocess.run(
            [sys.executable, "-m", "bgrealestate.dev_worker", "--once"],
            cwd=ROOT,
            env={"PYTHONPATH": str(ROOT / "src")},
            check=True,
        ),
        lambda: subprocess.run(
            [sys.executable, "-m", "bgrealestate.dev_scheduler", "--once"],
            cwd=ROOT,
            env={"PYTHONPATH": str(ROOT / "src")},
            check=True,
        ),
        lambda: subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=ROOT,
            env={"PYTHONPATH": str(ROOT / "src")},
            check=True,
        ),
    ]
    for check in checks:
        check()
    print("project validation ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
