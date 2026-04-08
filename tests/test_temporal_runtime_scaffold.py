from __future__ import annotations

import ast
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestTemporalRuntimeScaffold(unittest.TestCase):
    def test_temporal_runtime_module_is_syntax_valid(self) -> None:
        src = ROOT / "src" / "bgrealestate" / "workflows" / "temporal_runtime.py"
        ast.parse(src.read_text(encoding="utf-8"))

    def test_dev_worker_once_placeholder(self) -> None:
        env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "ENABLE_TEMPORAL_RUNTIME": "0"}
        r = subprocess.run(
            [sys.executable, "-m", "bgrealestate.dev_worker", "--once"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("placeholder mode active", r.stdout)

    def test_dev_scheduler_once_placeholder(self) -> None:
        env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "ENABLE_TEMPORAL_RUNTIME": "0"}
        r = subprocess.run(
            [sys.executable, "-m", "bgrealestate.dev_scheduler", "--once"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("placeholder mode active", r.stdout)

