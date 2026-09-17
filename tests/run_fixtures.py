#!/usr/bin/env python3
"""Run audit.py over tests/fixtures and compare FAIL counts to expected.json. Exit 1 on mismatch."""
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent / "skills" / "web-craft" / "scripts" / "audit.py"
expected = json.loads((HERE / "fixtures" / "expected.json").read_text())
bad = 0
for fname, checks in expected.items():
    r = subprocess.run([sys.executable, str(AUDIT), str(HERE / "fixtures" / fname), "--json"], capture_output=True, text=True)
    data = json.loads(r.stdout)
    got = {x["checker"]: len(x["fails"]) for x in data["results"]}
    for checker, n in checks.items():
        ok = got.get(checker) == n
        bad += not ok
        print(f"{'ok ' if ok else 'BAD'} {fname:<22} {checker:<12} expected {n} got {got.get(checker)}")
sys.exit(1 if bad else 0)
