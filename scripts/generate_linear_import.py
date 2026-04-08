from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "exports" / "linear-import-roadmap.csv"


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    print(f"linear backlog export ready: {SOURCE}")


if __name__ == "__main__":
    main()
