"""Golden-path script must skip cleanly without DB; must not require network."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestGoldenPathCheck(unittest.TestCase):
    def test_skips_without_database_url(self) -> None:
        env = os.environ.copy()
        env.pop("DATABASE_URL", None)
        env.setdefault("PYTHONPATH", str(ROOT / "src"))
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "golden_path_check.py")],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("SKIP", proc.stdout)
        self.assertIn("DATABASE_URL", proc.stdout)

    def test_skips_when_database_url_is_whitespace_only(self) -> None:
        env = os.environ.copy()
        env["DATABASE_URL"] = "   \t  "
        env.setdefault("PYTHONPATH", str(ROOT / "src"))
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "golden_path_check.py")],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("SKIP", proc.stdout)


if __name__ == "__main__":
    unittest.main()
